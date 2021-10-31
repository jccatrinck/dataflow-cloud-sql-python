from __future__ import division, print_function

import apache_beam as beam

import apache_beam as beam

import sqlalchemy
from sqlalchemy.orm import sessionmaker

class ReadFromDBFn(beam.DoFn):
    
    def __init__(self, url, query, query_params={}, *args, **kwargs):
        super(ReadFromDBFn, self).__init__(*args, **kwargs)
        self.url = url
        self.query = query
        self.query_params = query_params

    def process(self, data):
        data = dict(data)

        engine = sqlalchemy.create_engine(self.url, pool_timeout=10)

        query_params = self.query_params

        if 'db_query_params' in data:
            query_params = data['db_query_params']

        for record in engine.execute(sqlalchemy.sql.text(self.query), query_params):
            yield dict(record)

class WriteIntoDB(beam.PTransform):

    def __init__(self, url, table, update_ignores=(), *args, **kwargs):
        super(WriteIntoDB, self).__init__(*args, **kwargs)
        self.url = url
        self.table = table
        self.update_ignores = update_ignores

    def expand(self, pcoll):
        return pcoll | beam.ParDo(WriteIntoDBFn(
            url=self.url,
            table=self.table,
            update_ignores=self.update_ignores,
        ))

class WriteIntoDBFn(beam.DoFn):
    def __init__(self, url, table, update_ignores, *args, **kwargs):
        super(WriteIntoDBFn, self).__init__(*args, **kwargs)
        self.url = url
        self.table = table
        self.update_ignores = update_ignores
       
    @staticmethod               
    def column_reflect_listener(inspector, table, column_info):
        if isinstance(column_info['type'], sqlalchemy.dialects.postgresql.base.UUID):
            column_info['type'].as_uuid = True

    def start_bundle(self):
        engine = sqlalchemy.create_engine(self.url, pool_timeout=10)
        self.SessionClass = sessionmaker(bind=engine)
        self.session = self.SessionClass()
        engine = self.session.bind
        metadata = sqlalchemy.MetaData(bind=engine)
        self.table = sqlalchemy.Table(self.table, metadata, autoload=True, listeners=[
            ('column_reflect', self.column_reflect_listener)
        ])

    def process(self, data):
        try:
            insert_stmt = sqlalchemy.dialects.postgresql.insert(self.table) \
                .values(data) \
                .returning(sqlalchemy.sql.elements.literal_column('*'))
            cols = [col for col in insert_stmt.excluded if col.name not in self.update_ignores]
            update_columns = {col.name: col for col in cols}
            upsert_stmt = insert_stmt.on_conflict_do_update(
                index_elements=[col for col in self.table.primary_key],
                set_=update_columns
            )
            for rowproxy in self.session.execute(upsert_stmt).yield_per(1000):
                yield {col.name: getattr(rowproxy, col.name) for col in self.table.columns}
            self.session.commit()
        except:
            self.session.rollback()
            self.session.close()
            self.session.bind.dispose()
            raise

    def finish_bundle(self):
        self.session.close()
        self.session.bind.dispose()
        self.session = None