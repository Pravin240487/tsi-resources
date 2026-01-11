import boto3
import json
import os
import sys

def assume_role(role_arn, session_name="CrossAccountSession"):
    """Assume an AWS IAM role and return a boto3 session."""
    sts_client = boto3.client("sts")
    response = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName=session_name
    )
    creds = response["Credentials"]
    return boto3.Session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"]
    )

env = os.environ.get("Environment")
if env == "dev":
    account_id = "905418116080"
    account_ref = "dev"
elif env == "test":
    account_id = "637423349055"
    account_ref = "test"
elif env == "stage":
    account_id = "180294192430"
    account_ref = "stg"
elif env == "prod":
    account_id = "597088029926"
    account_ref = "prd"

role_arn = f"arn:aws:iam::{account_id}:role/oc-{account_ref}-ec1-da-stf-cross-account-iam-v1"
session = assume_role(role_arn)
sfn_client = session.client("stepfunctions", region_name="eu-central-1")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../.."))
SF_DIR = os.path.join(ROOT_DIR, "etl/sf_definition")
os.makedirs(SF_DIR, exist_ok=True)

# Use resolved account_id instead of os.environ['AWS_ACCOUNT_ID']
step_function_map = {
    "oc-common-ec1-da-batch-creation-stf-v1.json": f"arn:aws:states:eu-central-1:{account_id}:stateMachine:oc-{account_ref}-ec1-da-batch-creation-stf-v1",
    "oc-common-ec1-da-conversation-delta-stf-v1.json": f"arn:aws:states:eu-central-1:{account_id}:stateMachine:oc-{account_ref}-ec1-da-conversation-delta-stf-v1",
    "oc-common-ec1-da-flattening-stf-v1.json": f"arn:aws:states:eu-central-1:{account_id}:stateMachine:oc-{account_ref}-ec1-da-flattening-stf-v1",
    "oc-common-ec1-da-gap-processing-stf-v1.json": f"arn:aws:states:eu-central-1:{account_id}:stateMachine:oc-{account_ref}-ec1-da-gap-processing-stf-v1",
    "oc-common-ec1-da-intent-processing-stf-v1.json": f"arn:aws:states:eu-central-1:{account_id}:stateMachine:oc-{account_ref}-ec1-da-intent-processing-stf-v1",
    "oc-common-ec1-da-master-data-load-stf-v1.json": f"arn:aws:states:eu-central-1:{account_id}:stateMachine:oc-{account_ref}-ec1-da-master-data-load-stf-v1",
    "oc-common-ec1-da-rds-bronze-stf-v1.json": f"arn:aws:states:eu-central-1:{account_id}:stateMachine:oc-{account_ref}-ec1-da-rds-bronze-stf-v1",
    "oc-common-ec1-da-rds-silver-stf-v1.json": f"arn:aws:states:eu-central-1:{account_id}:stateMachine:oc-{account_ref}-ec1-da-rds-silver-stf-v1",
    "oc-common-ec1-da-rds-silver-state-execution-stf-v1.json": f"arn:aws:states:eu-central-1:{account_id}:stateMachine:oc-{account_ref}-ec1-da-rds-silver-state-execution-stf-v1",
    "oc-common-ec1-da-topic-processing-stf-v1.json": f"arn:aws:states:eu-central-1:{account_id}:stateMachine:oc-{account_ref}-ec1-da-topic-processing-stf-v1"
}

def download_step_function(definition_file, state_machine_arn):
    """Pull state machine definition from AWS and write to local file"""
    try:
        response = sfn_client.describe_state_machine(
            stateMachineArn=state_machine_arn
        )
        definition = response["definition"]

        definition_path = os.path.join(SF_DIR, definition_file)
        with open(definition_path, "w") as f:
            json.dump(json.loads(definition), f, indent=2)

        print(f"Downloaded {state_machine_arn} -> {definition_path}")
    except Exception as e:
        print(f"Failed to download {state_machine_arn}: {e}")
        raise

if __name__ == "__main__":
    failed = []
    for file_name, arn in step_function_map.items():
        try:
            download_step_function(file_name, arn)
        except Exception:
            failed.append(file_name)

    if failed:
        sys.exit(f"Failed to download: {', '.join(failed)}")
