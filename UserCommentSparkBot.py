import requests
import json
from itty import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tabledef import *

#For SQL database
engine = create_engine('sqlite:///brainSparkRequests.db', echo=False)
 
# create a Session
Session = sessionmaker(bind=engine)
session = Session()

#################################
# CHANGE VARIABLES TO MATCH BOT #
#################################
#managerRoomID = "Y2lzY29zcGFyazovL3VzL1JPT00vNGU1Yzk3YjAtNDQ3YS0xMWU4LWFjMjMtZjMwYWJmMTViZWNk"  #with Paulo
#managerRoomID = "Y2lzY29zcGFyazovL3VzL1JPT00vNGU3NTczNzAtNGM2OC0xMWU4LTg3NmEtNGYyZTM0MDAyNjRm"  #without Paulo
managerRoomID = "Y2lzY29zcGFyazovL3VzL1JPT00vOGRiN2I3NTAtODhkMS0xMWU4LTkzNzYtYzU0YzIzNDE1ZTdj" #Demo

ACCESS_TOKEN = "MjA1ODg3MGYtMWVhYi00OTBlLTkwYmQtZDUyOTAzODAzN2I4ZmU5NmRmNDAtY2Ex"
bot_email = "brainsparktest@sparkbot.io"
botName = "BrainSparkTest"


#Global variables, don't change:
conversationCounter = 0
commentList = []

#temp variable
test = True

def CreateRequest(_requestText, _requesterRoomId):
	ID = session.query(Request).count() + 1

	#confirm submission of question to user
	PostSparkMessage("Thank you for your feedback, we will respond as soon as possible. If you'd like to add anything to your feedback, please add #" + str(ID) + " to the message", _requesterRoomId)

	#create responseRoom
	responseRoomID = CreateSparkRoom(str(ID))

	#post to managerRoom and get id of the message
	messageId = PostSparkMessage("A new question has been asked: " + str(_requestText) + " --- Type '@" + str(botName) + " claim #" + str(ID) + "' in order to get added to the resolution Space for this question", managerRoomID)

	#Post all information to the db
	request = Request(_requesterRoomId, responseRoomID, messageId)
	session.add(request)
	session.commit()

	#post question in newly created room	
	PostSparkMessage("The following question was asked: " + _requestText, responseRoomID)
	PostSparkMessage("In order to reply to this question, please address the answer to @" + str(botName), responseRoomID)



def findRoom(the_header,room_name):
	roomId=None
	uri = 'https://api.ciscospark.com/v1/rooms'
	resp = requests.get(uri, headers=the_header)
	resp = resp.json()
	for room in resp["items"]:
		if room["title"] == room_name:
			roomId=None
			break
	return(roomId)

#Create a sparkroom to answer the question
def CreateSparkRoom(_requestID):
	global managerRoomID
	the_header = setHeaders()
	room_name = "resolve comment #" + _requestID

	roomId=findRoom(the_header,room_name)
	if roomId==None:
		roomInfo = {"title":room_name}
		uri = 'https://api.ciscospark.com/v1/rooms'
		resp = requests.post(uri, json=roomInfo, headers=the_header)
		var = resp.json()
		roomId = var["id"]

	return roomId

#Looks through the text to look for any #xxx and returns those in a set.
def FindTags(_text):
	tags = str(_text)
	print ""
	print tags
	print ""
	x = {tag.strip("#") for tag in tags.split() if tag.startswith("#")}
	return x.pop()

#Find the room that corresponds to the hashtag
def FindRoomToAdd(_text):
	roomFound = False
	tag = FindTags(_text)
	print tag

	#checks if a room for that tag exists.
	for x in session.query(Request).filter(Request.id == int(tag)):
		roomFound = True
		return x.resolutionRoomID
			
	if roomFound == False:
		return False

#Find the room that corresponds to the hashtag
def AddToExistingComment(_text, _userRoomID):
	commentFound = False
	tag = FindTags(_text)

	text = _text.replace("#" + tag + " ", "")
	text = text.replace("#" + tag, "")

	#checks if a room for that tag exists.
	for x in session.query(Request).filter(Request.id == int(tag)):
		if str(x.requesterID) == str(_userRoomID):
			commentFound = True
			PostSparkMessage("New message has been send by requester: " + text, x.resolutionRoomID)
			
	if commentFound == False:
		PostSparkMessage("room not found", _userRoomID)

#Add a user to the room
def AddToRoom(_roomID, _userID):
	header = setHeaders()
	member = {"roomId":_roomID,"personId": _userID, "isModerator": False}
	uri = 'https://api.ciscospark.com/v1/memberships'
	resp = requests.post(uri, json=member, headers=header)

#Post a spark message
def PostSparkMessage(message, roomId):
	header = setHeaders()
	message = {"roomId":roomId,"text":message}
	uri = 'https://api.ciscospark.com/v1/messages'
	resp = requests.post(uri, json=message, headers=header)
	var = resp.json()
	messageID = var["id"]
	return messageID

#Relay the message that was posted to the user who requested the case
def RelayManagerMessage(_message, _roomID):
		global botName
		#TODO: extract text and roomID from _message (for testing we user _message as being the text)
		text = _message.replace(botName + " ", "")
		roomID = _roomID
		roomFound = False

		for x in session.query(Request).filter(Request.resolutionRoomID == str(roomID)):
			roomFound = True
			PostSparkMessage("You've received the following response: " + text + " --- to respond, use #" + str(x.id), x.requesterID)
			PostSparkMessage("If this fully answered your question, type '#" + str(x.id) + " resolved'", x.requesterID)

		if roomFound == False:
			PostSparkMessage("Something has gone wrong with this request: requester ID not found", roomID)

#Create the Header for the Spark API
def setHeaders():         
    accessToken_hdr = 'Bearer ' + ACCESS_TOKEN
    spark_header = {'Authorization': accessToken_hdr, 'Content-Type': 'application/json; charset=utf-8'}
    return (spark_header)


def GetMessageText(_messageID):
	header = setHeaders()
	uri = "https://api.ciscospark.com/v1/messages/" + str(_messageID)
	resp = requests.get(uri, headers=header)
	resp = resp.json()
	tempText = resp["text"]
	text = json.dumps(tempText)
	
	text = text.strip('"')
	text = text.replace("\u2019", "\'")
	text = text.replace("\u201c", "\"")
	text = text.replace("\u201d", "\"")
	return text

def RemoveMessage(_messageId):
	header = setHeaders()
	uri = "https://api.ciscospark.com/v1/messages/" + str(_messageId)
	resp = requests.delete(uri, headers=header)


def CloseRoom(_roomID):
	header = setHeaders()
	uri = "https://api.ciscospark.com/v1/rooms/" + str(_roomID)
	resp = requests.delete(uri, headers=header)

def ResolveRoom(_text):
	tag = FindTags(_text)
	for x in session.query(Request).filter(Request.id == int(tag)):
		CloseRoom(x.resolutionRoomID)
		RemoveMessage(x.messageID)
		x.requesterID = None
        x.resolutionRoomID = None
        x.messageID = None
        session.commit()

@post('/')
def index(request):
	global managerRoomID
	global bot_email
	global botName
	webhook = json.loads(request.body) # get payload from webhook
	room_id = webhook['data']['roomId'] # get room id from message
	message_id = webhook['data']['id'] # get message id
	sender_id = webhook['data']['personId'] #get id of the sender
	sender_email = webhook['data']['personEmail']
	messageText = GetMessageText(message_id) #get text in the message


	if  str(sender_email) != str(bot_email):

		if str(room_id) == str(managerRoomID):
			if "claim #" in messageText.lower():
				roomID = FindRoomToAdd(messageText)
				if roomID != False:
					AddToRoom(roomID, sender_id)
				else:
					PostSparkMessage("Tag not found", managerRoomID)

		else:
			if "#" in messageText:
				if "resolved" in messageText.lower():
					ResolveRoom(messageText)

				else:
					AddToExistingComment(messageText, room_id)
				


			elif str(botName) in messageText:
				RelayManagerMessage(messageText, room_id)

			else:
				CreateRequest(messageText, room_id)

	return "true"

run_itty(server='wsgiref', host='0.0.0.0', port=10010)