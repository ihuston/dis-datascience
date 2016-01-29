__author__ = 'pivotal'
from dis_ds import parsing
import psycopg2
from dis_ds import parsing
import boto
from sqlalchemy import create_engine

def import_parsed_test_files(file_list):
    parsed_files_df= parse_file_list(file_list)
    engine=create_engine(postgres://pmgigyko:Mb7sR3WMZSNPYjm4FTvS0WRDhtqUgcam@pellefant.db.elephantsql.com:5432/pmgigyko')
    parsed_files_df.to_sql('disruptions_test1',engine)

def import_parsed_s3_files(file_prefix):
    parsed_s3_files_df=parse_s3_files(file_prefix)
    engine=create_engine(postgres://pmgigyko:Mb7sR3WMZSNPYjm4FTvS0WRDhtqUgcam@pellefant.db.elephantsql.com:5432/pmgigyko')
    parsed_s3_files_df.to_sql('disruptions_table',engine)


