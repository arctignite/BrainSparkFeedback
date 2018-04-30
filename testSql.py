import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tabledef import *
 
engine = create_engine('sqlite:///brainSparkRequests.db', echo=True)
 
# create a Session
Session = sessionmaker(bind=engine)
session = Session()
 
# Create objects  
user = Request("id3", "room3")
session.add(user)
 
user = Request("id4","room4")
session.add(user)
 
# commit the record the database
session.commit()