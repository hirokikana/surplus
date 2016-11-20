#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append('libs')
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import Config
Base = declarative_base()

from application import app

if __name__ == "__main__":
    config = Config()
    server_config = config.get_server_conf()
    db_uri = config.get_db_uri()
    engine = create_engine(db_uri, echo=True, encoding='utf-8')
    import pdb;pdb.set_trace()
    Base.metadata.create_all(engine)

    import route.static
    import route.api
    app.config['db_engine'] = engine

    session = sessionmaker(bind=engine)()
    app.config['session'] = session
    
    app.run(host=server_config['host'], port=server_config['port'], debug=True)
