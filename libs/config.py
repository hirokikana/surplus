from ConfigParser import SafeConfigParser

class Config():
    def __init__(self):
        self.parser = SafeConfigParser()
        self.parser.read("surplus.conf")

    def get_server_conf(self):
        return {'host':self.parser.get('server','host'),
                'port':int(self.parser.get('server','port'))}

    def get_db_uri(self):
        db_uri = '%s://%s:%s@%s/%s?charset=utf8' % (self.parser.get('database','engine'),
                                                    self.parser.get('database','user'),
                                                    self.parser.get('database','password'),
                                                    self.parser.get('database','host'),
                                                    self.parser.get('database','name'))
        return db_uri

