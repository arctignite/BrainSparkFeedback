from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
 
engine = create_engine('sqlite:///brainSparkRequests.db', echo=False)
Base = declarative_base()
 
########################################################################
class Request(Base):
    """"""
    __tablename__ = "request"

    id = Column(Integer, primary_key=True)
    requesterID = Column(String)
    resolutionRoomID = Column(String)
    messageID = Column(String)
 
    #----------------------------------------------------------------------
    def __init__(self, requesterID, resolutionRoomID, messageID):
        """"""
        self.requesterID = requesterID
        self.resolutionRoomID = resolutionRoomID
        self.messageID = messageID
 
# create tables
Base.metadata.create_all(engine)
