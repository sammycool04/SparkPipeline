import configparser
from datetime import datetime
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.functions import year, month, dayofmonth, hour, weekofyear, date_format


config = configparser.ConfigParser()
config.read('dl.cfg')

os.environ['AWS_ACCESS_KEY_ID']=config['KEYS']['AWS_ACCESS_KEY_ID']
os.environ['AWS_SECRET_ACCESS_KEY']=config['KEYS']['AWS_SECRET_ACCESS_KEY']


def create_spark_session():
    spark = SparkSession \
        .builder \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:2.7.0") \
        .getOrCreate()
    return spark


def process_song_data(spark, input_data, output_data):
#     song_data = input_data + "song_data/*/*/*/*.json"
    song_data = os.path.join("s3a://udacity-dend/", "song_data/A/A/A/*.json")
    # read song data file
    df = spark.read.json(song_data)

    # extract columns to create songs table
    songs_table = df.select("song_id","title","artist_id","year","duration").drop_duplicates()
    print(songs_table)

    # write songs table to parquet files partitioned by year and artist
    songs_table.write.parquet(output_data + "songs/", mode="overwrite", partitionBy =["year","artist_id"])

#     # extract columns to create artists table
    artists_table = df.select("artist_id","artist_name","artist_location","artist_latitude","artist_longitude").drop_duplicates()

#     # write artists table to parquet files
    artists_table.write.parquet(output_data + "artists/", mode="overwrite")


def process_log_data(spark, input_data, output_data):
    # get filepath to log data file
    log_data = input_data + log-data/*/*/*.json

    # read log data file
    df = spark.read.json(log_data)

    # filter by actions for song plays
    df = df.filter(df.page == 'NextSong')

    df.createOrReplaceTempView("log_data_table")

    # extract columns for users table
    users_table = spark.sql("""
                            SELECT DISTINCT userT.userId as user_id,
                            userT.firstName as first_name,
                            userT.lastName as last_name,
                            userT.gender as gender,
                            userT.level as level
                            FROM log_data_table userT
                            WHERE userT.userId IS NOT NULL
                        """)

    # write users table to parquet files
    users_table.write.parquet(os.path.join(output_data, "users/") , mode="overwrite")


    # create timestamp column from original timestamp column
    get_timestamp = udf(lambda x: x/1000, IntegerType())
    df = df.withColumn('start_time', get_timestamp('ts'))


    # create datetime column from original timestamp column
    get_datetime = udf(lambda x: from_unixtime(x), TimestampType())
    df = df.withColumn('datetime', from_unixtime('start_time'))

    # extract columns to create time table
    time_table = df.withColumn("hour",hour("start_time"))\
                    .withColumn("day",dayofmonth("start_time"))\
                    .withColumn("week",weekofyear("start_time"))\
                    .withColumn("month",month("start_time"))\
                    .withColumn("year",year("start_time"))\
                    .withColumn("weekday",dayofweek("start_time"))\
                    .select("ts","start_time","hour", "day", "week", "month", "year", "weekday").drop_duplicates()

    # write time table to parquet files partitioned by year and month
    time_table.parquet(os.path.join(output_data, "time_table/"), mode='overwrite', partitionBy=["year","month"])

    # read in song data to use for songplays table
    song_df = spark.read\
                .format("parquet")\
                .option("basePath", os.path.join(output_data, "songs/"))\
                .load(os.path.join(output_data, "songs/*/*/"))

    # extract columns from joined song and log datasets to create songplays table
    songplays_table =

    # write songplays table to parquet files partitioned by year and month
    songplays_table.mode('overwrite').partitionBy("year", "month").parquet(output_data+'songplays_table/')


def main():
    spark = create_spark_session()
    input_data = "s3a://udacity-dend/"
#     input_data = "data/"
    output_data = ""

    process_song_data(spark, input_data, output_data)
    process_log_data(spark, input_data, output_data)


if __name__ == "__main__":
    main()
