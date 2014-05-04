from datetime import datetime

from flask import current_app
from sqlalchemy import schema, types, orm
from sqlalchemy.engine import create_engine

# Database...
metadata = schema.MetaData()

url_table = schema.Table('shitbct_url', metadata,
    schema.Column('id',
        types.Integer,
        schema.Sequence('shitbct_url_seq_id', optional=True),
        primary_key=True),
    schema.Column('url', types.Unicode(2000)),
    schema.Column('url_title', types.Unicode(1024)),
    schema.Column('public', types.Boolean(), default=False),
    schema.Column('created_at', types.DateTime(), default=datetime.now)
)

config_table = schema.Table('shitbct_config', metadata,
    schema.Column('id',
        types.Integer,
        schema.Sequence('shitbct_config_seq_id', optional=True),
        primary_key=True),
    schema.Column('key', types.String),
    schema.Column('value', types.String)
)


class ShitBucketUrl(object):
    pass


class ShitBucketConfig(object):
    pass

orm.mapper(ShitBucketUrl, url_table)
orm.mapper(ShitBucketConfig, config_table)


def make_db_session(app):
    db_engine = create_engine(app.config['DB_URI'], echo=True)
    metadata.bind = db_engine
    metadata.create_all(checkfirst=True)

    session = orm.scoped_session(orm.sessionmaker(bind=db_engine,
                                                  autoflush=True,
                                                  autocommit=False,
                                                  expire_on_commit=True))
    return session
