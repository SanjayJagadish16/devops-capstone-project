"""
Account Service

This microservice handles the lifecycle of Accounts
"""
# pylint: disable=unused-import
from flask import jsonify, request, make_response, abort, url_for
from service.models import Account
from service.common import status  # HTTP Status Codes
from . import app  # Import Flask application

############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return jsonify(dict(status="OK")), status.HTTP_200_OK


############################################################
# Root URL
############################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Account REST API Service",
            version="1.0",
        ),
        status.HTTP_200_OK,
    )


############################################################
# Create a New Account
############################################################
@app.route("/accounts", methods=["POST"])
def create_accounts():
    """Creates an Account"""
    app.logger.info("Request to create an Account")
    check_content_type("application/json")

    account = Account()
    account.deserialize(request.get_json())
    account.create()
    message = account.serialize()

    location_url = url_for("get_account", account_id=account.id, _external=True)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


############################################################
# List All Accounts
############################################################
@app.route("/accounts", methods=["GET"])
def list_accounts():
    """List all Accounts"""
    app.logger.info("Request to list Accounts")

    accounts = Account.all()
    account_list = [account.serialize() for account in accounts]

    app.logger.info("Returning [%s] accounts", len(account_list))
    return jsonify(account_list), status.HTTP_200_OK


############################################################
# Read an Account
############################################################
@app.route("/accounts/<int:account_id>", methods=["GET"])
def get_account(account_id):
    """Reads an Account"""
    app.logger.info("Request to read an Account with id: %s", account_id)

    account = Account.find(account_id)
    if not account:
        abort(status.HTTP_404_NOT_FOUND, f"Account with id [{account_id}] could not be found.")

    return jsonify(account.serialize()), status.HTTP_200_OK


############################################################
# Update an Existing Account
############################################################
@app.route("/accounts/<int:account_id>", methods=["PUT"])
def update_account(account_id):
    """Updates an Account"""
    app.logger.info("Request to update an Account with id: %s", account_id)

    account = Account.find(account_id)
    if not account:
        abort(status.HTTP_404_NOT_FOUND, f"Account with id [{account_id}] could not be found.")

    check_content_type("application/json")
    account.deserialize(request.get_json())
    account.update()

    return jsonify(account.serialize()), status.HTTP_200_OK


############################################################
# Delete an Account
############################################################
@app.route("/accounts/<int:account_id>", methods=["DELETE"])
def delete_account(account_id):
    """Deletes an Account"""
    app.logger.info("Request to delete an Account with id: %s", account_id)

    account = Account.find(account_id)
    if account:
        account.delete()

    return "", status.HTTP_204_NO_CONTENT


############################################################
# Utility Function: Check Content-Type
############################################################
def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )
