from google.cloud import storage
import sys


# [END storage_list_buckets]
bucket_name = "voice-audio-1001"

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


if __name__ == "__main__":
    # create_bucket()
    if False:
        list_buckets()
        upload_blob(
            bucket_name=bucket_name,
            source_file_name=r"D:\vs-program\google\py\web-cloud\test\google\asr\resources\历代名人咏江阴_耳聆网.mp3",
            destination_blob_name="历代名人咏江阴_耳聆网_v1.mp3",
        )

    download_blob_into_memory(
        bucket_name=bucket_name,
        blob_name="a.txt"
    )






