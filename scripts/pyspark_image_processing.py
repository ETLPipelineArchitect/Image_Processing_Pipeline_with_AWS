from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf
from pyspark.sql.types import StringType
import cv2
import boto3
import numpy as np

# Initialize Spark Session
spark = SparkSession.builder.appName("ImageProcessingPipeline").getOrCreate()

# Read Metadata from S3
metadata_df = spark.read.json("s3://your-bucket/metadata/*.json")

# Define UDF for Image Transformation

def resize_image(image_key):
    s3 = boto3.client('s3')
    bucket = 'your-bucket'
    obj = s3.get_object(Bucket=bucket, Key=f'raw-images/{image_key}')
    img_bytes = obj['Body'].read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    resized_img = cv2.resize(img, (224, 224))
    _, img_encoded = cv2.imencode('.jpg', resized_img)
    return img_encoded.tobytes().hex()

resize_image_udf = udf(resize_image, StringType())

# Apply Image Transformation
processed_df = metadata_df.withColumn('resized_image', resize_image_udf(col('image_key')))
processed_df.show(5)

# Save Processed Data to S3 in Parquet Format
processed_df.write.parquet("s3://your-bucket/processed-images/", mode='overwrite')
