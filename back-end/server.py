# General API note: when an invalid request is sent by the client (ex. trying an invalid password/email combination) the status code of the response is set to 400

from flask import Flask
from flask import request
from flask import Response
from flask import abort
from flask import make_response
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask_cors import CORS, cross_origin
import json
from bson.objectid import ObjectId
from bson.json_util import dumps
import db_accounts as ac
import db_events as ev
import db_admin as ad
import internal as internal
import db_testing as TESTING
import db_skills as sk
# from flask_login import UserMixin
# from passlib.hash import sha256_crypt

# Connecting to MongoDB: 
# DB password: CPj0i24mLlKvkskt
# DB API key: mCh55pfNYQJMiQbeVKaljoU5CqDOdQp9aaGvo9IA8jxLhr9G22UvtSuy8LdFF64U (probably don't need this)
uri = "mongodb+srv://CMPT370Team25DB:CPj0i24mLlKvkskt@cmpt370db.godfxkb.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print("Error: connection to MongoDB failed!")
    print(e)

#Access database and collection "db_1" (placeholder collection)
db = client.CMPT370_Team25
my_collection = db["db_1"]
accounts_collection = db["accounts_collection"]
#accounts_collection = db["test_accounts"] # Used for testing; clear after use, leave only admin@admin.com
testing_accounts_collection = db["test_accounts"] #same as above, used for test methods that should never affect main collection
events_collection = db["events_collection"]
courses_collection = db["courses_collection"]
templates_collection =db["templates"]

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


def readDocuments(collection):
    """Example function for retrieving document. 

    Args:
        collection (Collection): collection to be accessed
    """
    result = collection.find()
    if result:
        for doc in result:
            print("Name: "+ doc['name'])
            print("Email: "+ doc['email'])
    else:
        print("Error: no documents found.")

# readDocuments(my_collection)

def addDocument(collection,doc):
    """Example function for adding a document to a collection.

    Args:
        collection (Collection): collection to be accessed
        doc (String): key-value pairs that define document
    """
    collection.insert_one(doc)

# newDocument = {"name":"John Doe", "email": "john@email.com", "age": 69}
# addDocument(my_collection,newDocument)

#app.config['CORS_HEADERS'] = 'Content-Type' # CORS setup

#Routes 
@app.route("/")
@cross_origin(origins='*')
def hello_world():
    return "Hello, World!"

@app.route('/get_id', methods=["POST"])
@cross_origin(origins='*')
def GetAccountID():
    """Retrieves the _id of an account from an email and password. An _id currently gives read/write access to most values in the account document. 
    Required request parameters: email, password

    Returns:
        Response: contains _id of database document with given email if successful, else has status_code 400
        Possible error messages: "Password does not match.", "Email not found."
    """
    return ac.get_account_id(request.get_json(), accounts_collection)

@app.route('/get_account_info',methods=["POST"])
@cross_origin(origins='*')
def GetAccountInfo():
    """Retrieves the account's information, excluding password, users (see /retrieve_family), and _id (see /get_id). 
    Required request arguments: _id

    Returns: 
        Response : contains the retrieved info
    Possible error messages: 
        "Error: account not found"
    """
    return ac.get_account_info(request.get_json(), accounts_collection)

@app.route("/get_user_info", methods=["POST"])
@cross_origin(origins="*")
def GetUserInfo():
    """Retrieves accounts info excluding password, using a childs ID
    
    
    Returns:
        Response

    Possible error messages:
        "Error: user does not exist"
    """
    return ac.get_user_info(request.get_json(), accounts_collection)


@app.route('/edit_subscriptions',methods=["POST"])
@cross_origin(origins='*')
def EditSubscriptions():
    """Changes the user's subscription settings. 
    Required request arguments: _id, prom, news

    Returns: 
    Possible error messages: 
        "Error: account not found"
    """
    return ac.edit_subscriptions(request.get_json(), accounts_collection)

@app.route('/admin_get_account_info',methods=["POST"])
@cross_origin(origins='*')
def AdminGetAccountInfo():
    """Retrieves the account's information, excluding password and _id. 
    Required request arguments: email, admin_ID
    Required staff level: 1

    Returns: 
        Response : contains the retrieved info
    Possible error messages: 
        "Error: admin account not found"
        "Error: user account not found"
        "Error: you do not have permission to perform this action"
    """
    return ad.get_account_info(request.get_json(), accounts_collection)


@app.route('/view_account_list',methods=["POST"])
@cross_origin(origins='*')
def ViewAccountList():
    """Returns a list of all account names.

    Returns:
        _type_: _description_
    """
    result = my_collection.find()
    response_body = ""
    if result:
        for doc in result:
            response_body = response_body +"\n" +((doc["name"]))
    else:
        print("Error: no documents found.")
    return response_body

@app.route("/submit_application", methods=["POST"])
@cross_origin(origins="*")
def SubmitAccount():
    """Endpoint for account registration; registers an account with provided information. 

    Returns:
        Response
    """
    return ac.submit_account(request.get_json(),accounts_collection)
    # return _corsify(ac.submit_account(request.get_json(),accounts_collection))

@app.route("/add_family", methods=["POST"])
@cross_origin(origins="*")
def AddFamily():
    """Endpoint for adding family member; adds a family member to account. 
    Required request parameters: name, birthday, _id

    Returns:
        Response
    """
    return ac.add_family(request.get_json(),accounts_collection)

@app.route("/remove_family", methods=["POST"])
@cross_origin(origins="*")
def DeleteFamily():
    """Endpoint for deleting family member; deletes a family member to account. 
    Required request parameters: name, _id

    Returns:
        Response
    
    Possible Responses (frontend should handle): 
        "User successfully removed"
        "Error: account not found"
        "Error: user not found"
        "Error: cannot delete parent"
    """
    return ac.delete_family(request.get_json(),accounts_collection,events_collection,courses_collection)

@app.route("/edit_family", methods=["POST"])
@cross_origin(origins="*")
def EditFamily():
    """Endpoint for adding editing family member; edits a family member's details. 
    Required request parameters: old_name, new_name, _id. To keep a field the same, send an empty string.

    Note: if new_name is already used, the user's name will not be changed and an error message will be sent as a response. However, all other modifications will still happen. 

    Returns:
        Response
            Possible response data: "Success", "Error: No user by that name found",  "Error: account not found", "Error: user with name already exists in account"
    """
    return ac.edit_family(request.get_json(),accounts_collection,events_collection,courses_collection)

@app.route("/retrieve_family", methods=["POST"])
@cross_origin(origins="*")
def RetrieveFamily():
    """Endpoint for getting list of family members associated with account. 
    Required request parameters: _id

    Returns: Response containing list of family members
    Possible error messages:
        "Error: account not found"
    """
    return ac.retrieve_family(request.get_json(),accounts_collection)

@app.route("/retrieve_events", methods=["POST"])
@cross_origin(origins="*")
def RetrieveEvents():
    """Endpoint for getting list of all events in database. 
    Required request parameters: none

    Returns:
        Response containing list of events
    """
    return ev.retrieve(request.get_json(), events_collection)

@app.route("/retrieve_courses", methods=["POST"])
@cross_origin(origins="*")
def RetrieveCourses():
    """Endpoint for getting list of all courses in database. 
    Required request parameters: none

    Returns:
        Response containing list of courses
    """
    return ev.retrieve(request.get_json(), courses_collection)

@app.route("/get_course", methods=["POST"])
@cross_origin(origins="*")
def GetCourse():
    """Endpoint for getting a single course.
    Required request parameters: name

    Returns:
        Response containing course JSON data
    Possible error messages:
        "Error: event not found"
    """
    return ev.get(request.get_json(), courses_collection)
    
@app.route("/get_event", methods=["POST"])
@cross_origin(origins="*")
def GetEvent():
    """Endpoint for getting a single event.
    Required request parameters: name

    Returns:
        Response containing event JSON data
    Possible error messages:
        "Error: event not found"
    """
    return ev.get(request.get_json(), events_collection)

@app.route("/add_event", methods=["POST"])
@cross_origin(origins="*")
def AddEvent():
    """Endpoint for adding an event.
    Required request parameters: account_ID, name, coach_email, desc, start, end, capacity
    Required staff level: 1

    Returns: Response
    Possible error messages:
        "Error: event name already exists"
        "Error: you do not have permission to perform this action"
        "Error: target coach account is not a staff account"
        "Error: coach account not found"
    """
    # TODO: add event parameters
    return ev.add(request.get_json(), events_collection, accounts_collection)

@app.route("/add_course", methods=["POST"])
@cross_origin(origins="*")
def AddCourse():
    """Endpoint for adding a course.
    Required request parameters: account_ID, name, coach_email, desc, start, end, capacity
    Required staff level: 1

    Returns: Response
    Possible error messages:
        "Error: event name already exists"
        "Error: you do not have permission to perform this action"
        "Error: target coach account is not a staff account"
        "Error: coach account not found"
    """
    # TODO: add event parameters
    # TODO: add event to coach's list of coached events 
    return ev.add(request.get_json(), courses_collection, accounts_collection)

@app.route("/edit_attendance", methods=["POST"])
@cross_origin(origins="*")
def EditAttendance():
    """Endpoint for updating attendance info.
    Required request parameters: account_ID, name, coach_email, attendance data
    Required staff level: 1

    Returns: Response
    Possible error messages:
        "Error: you do not have permission to perform this action"
        "Error: target coach account is not a staff account"
        "Error: coach account not found"
    """
    # TODO: add event parameters
    return ev.edit_attendance(request.get_json(), accounts_collection, events_collection, courses_collection)

@app.route("/add_course_user", methods=["POST"])
@cross_origin(origins="*")
def AddCourseToUser():
    """Endpoint for adding a course to a user's schedule. Also adds the user to the course's users list. 
    Required request parameters: _id, user_name, event_name

    Returns: Response
    Possible error messages:
        "Error: event not found"
        "Error: event already on user's event list"
        "Error: account not found"
        "Error: user not found"
        "Error: event full"
    """
    return ac.add_event(request.get_json(), accounts_collection, courses_collection, "course")

@app.route("/admin_add_course_user", methods=["POST"])
@cross_origin(origins="*")
def AdminAddCourseToUser():
    """Endpoint for adding a course to a user's schedule from an admin account. Also adds the user to the course's users list. 
    Required request parameters: admin_ID, email, user_name, event_name
    Required staff level: 1

    Returns: Response
    Possible error messages:
        "Error: event not found"
        "Error: event already on user's event list"
        "Error: target account not found"
        "Error: admin account not found"
        "Error: user not found"
        "Error: you do not have permission to perform this action"
        "Error: event full"
    """
    return ad.add_event_user(request.get_json(), accounts_collection, courses_collection, "course")

@app.route("/admin_add_event_user", methods=["POST"])
@cross_origin(origins="*")
def AdminAddEventToUser():
    """Endpoint for adding an event to a user's schedule from an admin account. Also adds the user to the event's users list. 
    Required request parameters: admin_ID, email, user_name, event_name
    Required staff level: 1

    Returns: Response
    Possible error messages:
        "Error: event not found"
        "Error: event already on user's event list"
        "Error: target account not found"
        "Error: admin account not found"
        "Error: user not found"
        "Error: you do not have permission to perform this action"
        "Error: event full"
    """
    return ad.add_event_user(request.get_json(), accounts_collection, events_collection, "event")
    
@app.route("/add_event_user", methods=["POST"])
@cross_origin(origins="*")
def AddEventToUser():
    """Endpoint for adding a course to a user's schedule.
    Required request parameters: _id, user_name, event_name

    Returns: Response
    Possible error messages:
        "Error: event not found"
        "Error: event already on user's event list"
        "Error: account not found"
        "Error: user not found"
        "Error: event full"
    """
    return ac.add_event(request.get_json(), accounts_collection, events_collection, "event")

@app.route("/remove_event_user", methods=["POST"])
@cross_origin(origins="*")
def RemoveEventFromUser():
    """Endpoint for removing an event from a user's schedule and removing that user from the event's enrolled list.
    Required request parameters: _id, user_name, event_name

    Returns: Response
    Possible error messages:
        "Error: event not on user's list"
        "Error: account not found"
        "Error: user not found"
        "Error: event not found"
    """
    return ac.remove_event(request.get_json(), accounts_collection, events_collection, "event")

@app.route("/remove_course_user", methods=["POST"])
@cross_origin(origins="*")
def RemoveCourseFromUser():
    """Endpoint for removing a course from a user's schedule and removing that user from the event's enrolled list.
    Required request parameters: _id, user_name, event_name

    Returns: Response
    Possible error messages:
        "Error: event not on user's list"
        "Error: account not found"
        "Error: user not found"
        "Error: event not found"
    """
    return ac.remove_event(request.get_json(), accounts_collection, courses_collection, "course")

@app.route("/admin_remove_event_user", methods=["POST"])
@cross_origin(origins="*")
def AdminRemoveEventFromUser():
    """Endpoint for adding an event to a user's schedule.
    Required request parameters: admin_ID, email, user_name, event_name

    Returns: Response
    Possible error messages:
        "Error: event not found"
        "Error: target account not found"
        "Error: admin account not found"
        "Error: user not found"
        "Error: you do not have permission to perform this action"
    """
    return ad.remove_event(request.get_json(), accounts_collection, events_collection, "event")

@app.route("/admin_remove_course_user", methods=["POST"])
@cross_origin(origins="*")
def AdminRemoveCourseFromUser():
    """Endpoint for adding an event to a user's schedule.
    Required request parameters: admin_ID, email, user_name, event_name

    Returns: Response
    Possible error messages:
        "Error: event not found"
        "Error: target account not found"
        "Error: admin account not found"
        "Error: user not found"
        "Error: you do not have permission to perform this action"
    """
    return ad.remove_event(request.get_json(), accounts_collection, courses_collection, "course")

@app.route("/retrieve_user_events", methods=["POST"])
@cross_origin(origins="*")
def RetrieveUserEvents():
    """Endpoint for getting list of events user is enrolled in. 
    Required request parameters: account_ID, name

    Returns: Response containing list of events user is enrolled in
    Possible error messages:
        "Error: account not found"
        "Error: user not found"
    """
    return (ac.retrieve_enrollments(request.get_json(), "events", accounts_collection))

@app.route("/retrieve_user_courses", methods=["POST"])
@cross_origin(origins="*")
def RetrieveUserCourses():
    """Endpoint for getting list of events user is enrolled in. 
    Required request parameters: account_ID, name

    Returns: Response containing list of courses user is enrolled in
    Possible error messages:
        "Error: account not found"
        "Error: user not found"
    """
    return (ac.retrieve_enrollments(request.get_json(), "courses", accounts_collection))

@app.route("/retrieve_account_events", methods=["POST"])
@cross_origin(origins="*")
def RetrieveAccountEvents():
    """Endpoint for getting account's users and their events. Technically redundant; /retrieve_family already contains all user info, including events.
    Required request parameters: account_ID

    Returns: Response: list where each entry has a user's "_id", a user's "name", and a user's "events" (list of events, may be empty)
    Possible error messages:
        "Error: account not found"
    """
    return (ac.retrieve_account_enrollments(request.get_json(), "events", accounts_collection))

@app.route("/retrieve_account_courses", methods=["POST"])
@cross_origin(origins="*")
def RetrieveAccountCourses():
    """Endpoint for getting account's users and their courses. Technically redundant; /retrieve_family already contains all user info, including courses.
    Required request parameters: account_ID

    Returns: Response: list where each entry has a user's "_id", a user's "name", and a user's "events" (list of courses, may be empty)
    Possible error messages:
        "Error: account not found"
    """
    return (ac.retrieve_account_enrollments(request.get_json(), "courses", accounts_collection))

@app.route("/delete_event", methods=["POST"])
@cross_origin(origins="*")
def DeleteEvent():
    """Deletes event from event list. 
    Required request parameters: event_name, account_ID
    Required staff level: 1

    Returns: Response
    Possible error messages: 
        "Error: event not found"
        "Error: you do not have permission to perform this action"
        "Error: account not found"
    """
    return ev.delete(request.get_json(), events_collection,accounts_collection,"event")

@app.route("/delete_course", methods=["POST"])
@cross_origin(origins="*")
def DeleteCourse():
    """
    Deletes event from event list. 
    Required request parameters: event_name, account_ID
    Required staff level: 1

    Returns: Response
    Possible error messages: 
        "Error: event not found"
        "Error: you do not have permission to perform this action"
        "Error: account not found"
    """
    return ev.delete(request.get_json(), courses_collection, accounts_collection, "course")

@app.route("/change_staff_level", methods=["POST"])
@cross_origin(origins="*")
def ChangeStaffLevel():
    """Changes an account's staff level to the given value.
    Required request arguments: admin_ID (account ID of logged-in admin account), email (email of account to be changed), level
    Required staff level: 3

    Customer=0
    Coach=1
    [placeholder]=2
    Admin=3
    
    Returns: Response
    Possible error messages: 
        "Error: admin account not found"
        "Error: user account not found"
        "Error: you do not have permission to perform this action"
        "Error: target account's staff level is too high to change."
    """
    return ad.change_staff_level(request.get_json(),accounts_collection)

@app.route("/get_all_accounts", methods=["POST"])
@cross_origin(origins="*")
def GetAllAccounts():
    """Returns a list containing a dictionary for each account in the database. Each dictionary contains the email and staffLevel of the account.
    Required request arguments: admin_ID
    Required staff level: 1
    
    Returns: Response
    Possible error messages: 
        "Error: admin account not found"
        "Error: you do not have permission to perform this action"
    """
    return ad.get_all_accounts(request.get_json(),accounts_collection)


@app.route("/get_all_account_id", methods=["POST"])
@cross_origin(origins="*")
def GetAllAccountsObject():
    """Returns a list of all the account user ID's.
    requires admin_ID
    requires staff level: 1

    Returns: Response
    Possible error messages:
        "Error: admin account not found"
        "Error: you do not have permission to perform this action"
    """
    return ad.get_account_object_list(request.get_json(), accounts_collection)

@app.route("/change_level", methods=["POST"])
@cross_origin(origins="*")
def ChangeLevel():
    """Decrements, increments, or sets a user's level. 
    Required request arguments: admin_ID, email, name, level
    Required staff level: 1
    The 'level' argument can be:
        "+": increases user's level by one
        "-": decreases user's level by one (if possible)
        int: sets the user's level to given integer
    
    Returns: Response
    Possible error messages: 
        "Error: admin account not found"
        "Error: you do not have permission to perform this action"
        "Error: user account not found"
        "Error: user's level is too low to decrement"
        "Error: invalid request"
        "Error: user not found"
    """
    return ad.change_level(request.get_json(),accounts_collection)

@app.route('/update_skills_templates', methods=["POST"])
@cross_origin(origins="*")
def UpdateSkillTemplates():
    """Updates all users to have a skill list matching the skill template stored in the database. 
    If user already has a skill on their list, keeps it
    If user did not already have a skill on their list, adds it
    If user has a skill that's not in the template (based on name), deletes it 
    You should call this method through Postman once if you update the skills list template.
    Required request arguments: _id (requires staff level >0)

    Returns: response
    Possible error messages:
        "Error: you do not have permission to perform this action
        "Error: admin account not found"
    """
    return sk.update_skill_template(request.get_json(), templates_collection, accounts_collection)

@app.route('/get_skills', methods=["POST"])
@cross_origin(origins="*")
def GetSkills():
    """Retrieves the skills of all users, in format {<user1's name>:<skill object>,...}
    Required request parameters: email, _id
    The method is allowed if the account of the _id is a staff account or if the _id matches the _id of email's account (i.e. customers can see their own family's skills, but not anyone else's)

    Returns: response
    Possible error messages:
        "Error: you do not have permission to perform this action"
        "Error: account not found (from _id)"
        "Error: account not found (from email)"
    """
    return sk.get_skills(request.get_json(), accounts_collection)

@app.route('/toggle_skills', methods=["POST"])
@cross_origin(origins="*")
def ToggleSkills():
    """Toggles whether or not a user's skill is checked. 
    Required request parameters: email, _id, user_name, toggle_list 
    toggle_list is a [list] of skill names (strings) that should be toggled

    Returns: response
    Possible error messages:
        "Error: you do not have permission to perform this action"
        "Error: account not found" #This can happen if the user isn't in the account
        "Error: admin account not found"
    """
    return sk.toggle_skills(request.get_json(), accounts_collection)

#TODO: UNTESTED 
@app.route('/check_uncheck_skills', methods=["POST"])
@cross_origin(origins="*")
def CheckUncheckSkills():
    """Changes the True/False state of skills. 
    Required request parameters: email, _id, user_name, check_list, uncheck_list
    check_list is a [list] of skill names (strings) that should be turned on
    uncheck_list is a [list] of skill names (strings) that should be turned off


    Returns: response
    Possible error messages:
        "Error: you do not have permission to perform this action"
        "Error: account not found" #This can happen if the user isn't in the account
        "Error: admin account not found"
    """
    return sk.check_skills(request.get_json(), accounts_collection)

@app.route('/change_account_info', methods=["POST"])
@cross_origin(origins="*")
def ChangeAccountInfo():
    """Changes account information. Send empty string to leave value the same.
    Required request parameters: old_email, new_email, _id (of admin), phone, staff_level

    Returns: response
    Possible error messages:
        "Error: you do not have permission to perform this action"
        "Error: user account not found"
        "Error: admin account not found"
    """
    return ad.change_account_info(request.get_json(), accounts_collection)

@app.route('/change_user_info', methods=["POST"])
@cross_origin(origins="*")
def ChangeUserInfo():
    """Changes user information. Send empty string to leave value the same.
    Required request parameters: email, _id (of admin), old_name, new_name, level, birthday

    Returns: response
    Possible error messages:
        "Error: you do not have permission to perform this action"
        "Error: user account not found"
        "Error: admin account not found"
    """
    return ad.change_user_info(request.get_json(), accounts_collection)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#
#
#TODO: TESTING, remove for production
@app.route("/test_add_admin", methods=["POST"])
@cross_origin(origins="*")
def TestAddAdmin():
    return TESTING.add_admin(testing_accounts_collection)

@app.route("/test_add_skill_account", methods=["POST"])
@cross_origin(origins="*")
def TestAddSkillsAccount():
    return TESTING.add_skill_test_account(testing_accounts_collection)

@app.route("/test_clear_collection", methods=["POST"])
@cross_origin(origins="*")
def TestClearCollection():
    return TESTING.clear_collection(testing_accounts_collection)

@app.route("/test_delete", methods=["POST"])
@cross_origin(origins="*")
def TestDelete():
    return internal.clear_user_schedule(request.get_json()["_id"],courses_collection,events_collection)

@app.route("/get_account_ids_test", methods=["POST"])
@cross_origin(origins="*")
def GetAccountIDTest():
    return TESTING.get_account_ids_test(testing_accounts_collection)

@app.route("/create_password_test_accounts", methods=["POST"])
@cross_origin(origins="*")
def CreatePasswordTestAccounts():
    return TESTING.create_password_test_accounts(testing_accounts_collection)

def _corsify(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response



if(__name__ == "__main__"):
    app.run(debug=True)

# Connects to database
database = db.DB_Connection()


# To run: cd into the back-end directory (Alternatively, edit your paths into start server.ahk, compile, run, and use hotkey in powershell)

# Set-ExecutionPolicy Unrestricted -Scope Process
# (Allows you to run the script to start the venv)

# .\windowsVenv\Scripts\activate
# to actually start the venv

# py server.py
# to actually run the back end server

# Kiran: When I tried to run the front end I got an error: 'error:03000086:digital envelope routines::initialization error'
#Fix was to run the following in the terminal 
#set NODE_OPTIONS=--openssl-legacy-provider

# CAN USE .\Startup.ps1 in powershell (while in backend) to start the server


#CTRL + c to stop the local server




######### TO RUN THE FRONT END ##########

# cd into front-end
# npm start
