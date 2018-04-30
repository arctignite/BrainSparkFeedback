import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tabledef import *
 
engine = create_engine('sqlite:///brainSparkRequests.db', echo=True)
 
# create a Session
Session = sessionmaker(bind=engine)
session = Session()
 
# Create objects  
user = Student("id1", "room1")
session.add(user)
 
user = Student("id2","room2")
session.add(user)
 
# commit the record the database
session.commit()