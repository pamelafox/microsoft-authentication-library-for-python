# Copyright (c) Microsoft Corporation.
# All rights reserved.
#
# This code is licensed under the MIT License.
import json
import logging
import os
import time
try:  # Python 2
    from urlparse import urlparse
except:  # Python 3
    from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def _scope_to_resource(scope):  # This is an experimental reasonable-effort approach
    u = urlparse(scope)
    if u.scheme:
        return "{}://{}".format(u.scheme, u.netloc)
    return scope  # There is no much else we can do here


def _obtain_token(http_client, resource, client_id=None):
    if "IDENTITY_ENDPOINT" in os.environ and "IDENTITY_HEADER" in os.environ:
        return _obtain_token_on_app_service(
            http_client, os.environ["IDENTITY_ENDPOINT"], os.environ["IDENTITY_HEADER"],
            resource, client_id=client_id)
    return _obtain_token_on_azure_vm(http_client, resource, client_id=client_id)


def _obtain_token_on_azure_vm(http_client, resource, client_id=None):
    # Based on https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/how-to-use-vm-token#get-a-token-using-http
    logger.debug("Obtaining token via managed identity on Azure VM")
    params = {
        "api-version": "2018-02-01",
        "resource": resource,
        }
    if client_id:
        params["client_id"] = client_id
    resp = http_client.get(
        "http://169.254.169.254/metadata/identity/oauth2/token",
        params=params,
        headers={"Metadata": "true"},
        )
    try:
        payload = json.loads(resp.text)
        if payload.get("access_token") and payload.get("expires_in"):
            return {  # Normalizing the payload into OAuth2 format
                "access_token": payload["access_token"],
                "expires_in": int(payload["expires_in"]),
                "resource": payload.get("resource"),
                "token_type": payload.get("token_type", "Bearer"),
                }
        return payload  # Typically an error
    except ValueError:
        logger.debug("IMDS emits unexpected payload: %s", resp.text)
        raise

def _obtain_token_on_app_service(http_client, endpoint, identity_header, resource, client_id=None):
    # Prerequisite: Create your app service https://docs.microsoft.com/en-us/azure/app-service/quickstart-python
    # Assign it a managed identity https://docs.microsoft.com/en-us/azure/app-service/overview-managed-identity?tabs=portal%2Chttp
    # SSH into your container for testing https://docs.microsoft.com/en-us/azure/app-service/configure-linux-open-ssh-session
    logger.debug("Obtaining token via managed identity on Azure App Service")
    params = {
        "api-version": "2019-08-01",
        "resource": resource,
        }
    if client_id:
        params["client_id"] = client_id
    resp = http_client.get(
        endpoint,
        params=params,
        headers={
            "X-IDENTITY-HEADER": identity_header,
            "Metadata": "true",  # Unnecessary yet harmless for App Service,
            # It will be needed by Azure Automation 
            # https://docs.microsoft.com/en-us/azure/automation/enable-managed-identity-for-automation#get-access-token-for-system-assigned-managed-identity-using-http-get
            },
        )
    try:
        payload = json.loads(resp.text)
        if payload.get("access_token") and payload.get("expires_on"):
            return {  # Normalizing the payload into OAuth2 format
                "access_token": payload["access_token"],
                "expires_in": int(payload["expires_on"]) - int(time.time()),
                "resource": payload.get("resource"),
                "token_type": payload.get("token_type", "Bearer"),
                }
        return {
            "error": "invalid_scope",  # Empirically, wrong resource ends up with a vague statusCode=500
            "error_description": "{}, {}".format(
                payload.get("statusCode"), payload.get("message")),
            }
    except ValueError:
        logger.debug("IMDS emits unexpected payload: %s", resp.text)
        raise

