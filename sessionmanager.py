# Gabriel Whatley - 3/10/2024
import uuid
import datetime


class SessionManager:
    #  This object manages a dictionary. The length of the dictionary is capped at the length specified during
    #  instantiation. When a new key is added to the dictionary, the oldest key/value pair is deleted.

    def __init__(self, max_sessions: int):
        self.max_sessions = max_sessions  # Store an integer to determine the max depth of the dictionary.
        self.session_dict = {}  # Create a list to store the dictionaries of session data.

    def newsession(self) -> str:  # Generate a new session key, store it in the dictionary and return the generated key.
        self.__cleanup()  # Attempt to trim dictionary length based on the requested length.
        session_id = str(uuid.uuid4())  # Generate a new completely random session ID.
        self.session_dict[session_id] = (None, None, None)  # Store the new session ID as a key the dictionary and initialize an empty tuple (manu_name, exp_date, lot_no)
        return session_id  # Return the session ID to the caller for use in a cookie.

    def setquery(self, session_id: str, manu_name: str = None, exp_date: str = None, lot_no: str = None):
        if exp_date is not None:  # Only convert exp_date to datetime if it has a value, converting a None will cause a crash.
            exp_date = datetime.datetime.strptime(exp_date, "%Y-%m-%d")  # Convert string produced by form to datetime for use with pymongo.
        self.session_dict.update({session_id: (manu_name, exp_date, lot_no)})  # Update the session in the dict with the tuple.

    def getquery(self, session_id: str) -> (str, datetime, str):
        return self.session_dict.get(session_id)  # Unpack manu_name, exp_date, lot_no from tuple for this session_id.

    def __cleanup(self):  # Trims the dictionary to the specified amount of max_sessions.
        keys = list(self.session_dict.keys())  # Convert the session IDs (keys) in the dictionary to a list.
        if len(keys) >= self.max_sessions:  # If length of list of keys is longer than the max allowed length.
            self.session_dict.pop(keys[0])  # Delete the oldest key pair from the dictionary.
