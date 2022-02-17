
PROJECT_ID=jk-mlops-dev
PROJECT_NUMBER=$(gcloud projects list --filter="projectId:$PROJECT_ID" --format="value(PROJECT_NUMBER)")
REGION=us-central-1
GCS_BUCKET=gs://jk-alphafold-staging

FILESTORE_ID=jkalphafold
FILE_SHARE_NAME=datasets_v1
ZONE=us-central1-a
NETWORK=projects/${PROJECT_NUMBER}/global/networks/default

gcloud filestore instances create $FILESTORE_ID \
    --location=$ZONE \
    --tier=STANDARD \
    --file-share=name="$FILE_SHARE_NAME,capacity=3TB" \
    --network=name=$NETWORK,connect-mode=PRIVATE_SERVICE_ACCESS


PEERING_RANGE_NAME=google-reserved-range
NETWORK=default
# NOTE: `prefix-length=16` means a CIDR block with mask /16 will be
# reserved for use by Google services, such as Vertex AI.
gcloud compute addresses create $PEERING_RANGE_NAME \
  --global \
  --prefix-length=16 \
  --description="peering range for Google service" \
  --network=$NETWORK \
  --purpose=VPC_PEERING

# Create the VPC connection.
gcloud services vpc-peerings connect \
  --service=servicenetworking.googleapis.com \
  --network=$NETWORK \
  --ranges=$PEERING_RANGE_NAME \
  --project=$PROJECT_ID