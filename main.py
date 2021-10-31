from __future__ import division, print_function, absolute_import
import os
import logging
import argparse
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions

from transformations.db import ReadFromDBFn

def read_file(filename):
    with open(filename, 'r') as f:
        content = f.read()
        f.close()
        return content

def run():
    # get the cmd args
    args, pipeline_args = get_args()

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = args.service_account_file

    # Create the pipeline
    options = PipelineOptions(pipeline_args)
    options.view_as(SetupOptions).save_main_session = True
    with beam.Pipeline(options=options) as p:
        query = read_file('./sql/query.sql')

        (
            p
            | "Initialize" >> beam.Create([{}])
            | "Reading tables" >> beam.ParDo(ReadFromDBFn(
                url=args.db_url,
                query=query,
            ))
            | "Log tables" >> beam.Map(lambda item: logging.info(item))
        )

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--service-account-file', dest='service_account_file')
    parser.add_argument('--db-url', dest='db_url')

    return parser.parse_known_args()


if __name__ == '__main__':
    run()
