from pyspark.sql import SparkSession

# Initialize Spark Session
spark = SparkSession.builder.appName("ImageAnalysisPipeline").getOrCreate()

# Load Processed Data
processed_data_path = "s3://your-bucket/processed-images/*.parquet"
data_df = spark.read.parquet(processed_data_path)

data_df.createOrReplaceTempView("image_data")

# Top 10 Most Common Labels
common_labels = spark.sql("""
  SELECT label, COUNT(*) as count
  FROM image_data
  LATERAL VIEW explode(labels) as label
  GROUP BY label
  ORDER BY count DESC
  LIMIT 10
""")
common_labels.show()

# Count Images by Creator
images_by_creator = spark.sql("""
  SELECT creator, COUNT(*) as image_count
  FROM image_data
  GROUP BY creator
  ORDER BY image_count DESC
""")
images_by_creator.show()

# Save Query Results to S3
common_labels.write.csv("s3://your-bucket/metadata/output/top_labels.csv", mode='overwrite')
images_by_creator.write.csv("s3://your-bucket/metadata/output/images_by_creator.csv", mode='overwrite')
