from google.cloud import storage
import sys

def list_buckets():
    """Lists all buckets."""

    storage_client = storage.Client()
    buckets = storage_client.list_buckets()

    for bucket in buckets:
        print(bucket.name)


# [END storage_list_buckets]
bucket_name = "voice-audio-1001"
def create_bucket():
    # [START storage_quickstart]

    # Instantiates a client
    storage_client = storage.Client()

    # 使用更具唯一性的存储桶名称，比如加入项目ID和时间戳
    # bucket_name = "voice-audio-human-ai-454609"
    bucket_name = "voice-audio-1001"

    # Creates the new bucket
    bucket = storage_client.create_bucket(bucket_name)

    print(f"Bucket {bucket.name} created.")
    # [END storage_quickstart]

def upload_blob(bucket_name, source_file_name, destination_blob_name):

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Optional: set a generation-match precondition to avoid potential race conditions
    # and data corruptions. The request to upload is aborted if the object's
    # generation number does not match your precondition. For a destination
    # object that does not yet exist, set the if_generation_match precondition to 0.
    # If the destination object already exists in your bucket, set instead a
    # generation-match precondition using its generation number.
    generation_match_precondition = 0

    blob.upload_from_filename(source_file_name, if_generation_match=generation_match_precondition)

    print(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )

def download_blob(bucket_name, source_blob_name, destination_file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(
        "Downloaded storage object {} from bucket {} to local file {}.".format(
            source_blob_name, bucket_name, destination_file_name
        )
    )

def download_blob_into_memory(bucket_name, blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    contents = blob.download_as_bytes()

    print(
        "Downloaded storage object {} from bucket {} as the following bytes object: {}.".format(
            blob_name, bucket_name, contents.decode("utf-8")
        )
    )

def download_public_file(bucket_name, source_blob_name, destination_file_name):
    storage_client = storage.Client.create_anonymous_client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(
        "Downloaded public blob {} from bucket {} to {}.".format(
            source_blob_name, bucket.name, destination_file_name
        )
    )


if __name__ == "__main__":
    # create_bucket()
    if False:
        list_buckets()
        upload_blob(
            bucket_name=bucket_name,
            source_file_name=r"D:\vs-program\google\py\web-cloud\test\google\asr\resources\历代名人咏江阴_耳聆网.mp3",
            destination_blob_name="历代名人咏江阴_耳聆网_v1.mp3",
        )

    download_blob(
        bucket_name=bucket_name,
        source_blob_name="历代名人咏江阴_耳聆网_v1.mp3",
        destination_file_name="1111.mp3",
    )






