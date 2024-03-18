# Gabriel Whatley - 3/10/2024
import uuid


class SessionManager:
    #  This object manages a dictionary. The length of the dictionary is capped at the length specified during
    #  instantiation. When a new key is added to the dictionary, the oldest key/value pair is deleted.

    def __init__(self, max_sessions: int):
        self.max_sessions = max_sessions  # Store an integer to determine the max depth of the dictionary.
        self.session = {}  # Create a dictionary to store sessionID/QueryResult pairs.

    def newsession(self) -> str:  # Generate a new session key, store it in the dictionary and return the generated key.
        self.__cleanup()  # Attempt to trim dictionary length based on the requested length.
        session_id = str(uuid.uuid4())  # Generate a new completely random session ID.
        self.session[session_id] = None  # Store the new session ID as a key the dictionary with an empty value
        return session_id  # Return the session ID to the caller for use in a cookie.

    def addresult(self, session_id: str, query_results: object):  # Store query results based on a session ID.
        self.session.update({session_id: query_results})

    def getresult(self, session_id: str) -> object:  # Get the query results tied to the sessionID
        return self.session.get(session_id)

    def __cleanup(self):  # Trims the dictionary to the specified amount of max_sessions.
        keys = list(self.session.keys())  # Convert the session IDs (keys) in the dictionary to a list.
        if len(keys) >= self.max_sessions:  # If length of list of keys is longer than the max allowed length.
            self.session.pop(keys[0])  # Delete the oldest key pair from the dictionary.
