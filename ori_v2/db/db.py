import uuid
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from ori_v2.db.schema import Base

class Database:
    def __init__(self):
        self.url = URL.create(
            drivername="postgresql",
            username="root",
            password="mysecretpassword",
            database="local",
            host="localhost",
            port="5432",
        )

        self.engine = create_engine(self.url)
        self.Session = sessionmaker(bind=self.engine)

    @staticmethod
    def uuid():
        return str(uuid.uuid4())

    def create_tables(self):
        # First delete all tables
        Base.metadata.drop_all(self.engine)

        # Then create all tables
        Base.metadata.create_all(self.engine)
