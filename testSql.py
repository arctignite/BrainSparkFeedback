import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tabledef import *
 
engine = create_engine('sqlite:///brainSparkRequests.db', echo=True)
 
# create a Session
Session = sessionmaker(bind=engine)
session = Session()
 
# Create objects  
request = Request("id3", "room3")
session.add(request)
 
request = Request("id4","room4")
session.add(request)
 
# commit the record the database
session.commit()