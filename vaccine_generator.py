import random
import string
import pymongo
import datetime

client = pymongo.MongoClient("mongodb+srv://vaccine_buddy_user:Br4bODkOhkhvcOU0@cluster0.2efzlbn.mongodb.net/?retryWrites=true&w=majority")
mydb = client["vaccine_buddy"]  # Name of the database.
mycol = mydb["inventory"]  # Name of the collection.

month_end_dict = {  # Dictionary to tell how many days are in each month in 2024.
	1: 31,
	2: 29,
	3: 31,
	4: 30,
	5: 31,
	6: 30,
	7: 31,
	8: 31,
	9: 30,
	10: 31,
	11: 30,
	12: 31,
}


def random_letters(length: int) -> string:  # Generate a string of random uppercase letters with user defined length.
	random_letters_id = ""  # Create string to store the result
	for i in range(length):  # Loop as many times as specified by argument.
		random_letters_id += random.choice(string.ascii_uppercase)  # Append a random letter to the end of the string.
	return random_letters_id


def random_numbers(length: int) -> string:  # Generate a string of random numbers with user defined length.
	random_numbers_id = ""  # Create string to store the result
	for i in range(length):  # Loop as many times as specified by argument.
		random_numbers_id += random.choice(string.digits)  # Append a random letter to the end of the string.
	return random_numbers_id


def cleardatabase() -> int:  # Deletes the documents contained in a query object from the database.
	result = mycol.delete_many({})
	return result.deleted_count


def generate_vaccines(amount: int):  # Generate random vaccine test data and add it to the database.
	for i in range(0, amount):  # Loop number of times specified by user.
		manu_num = round(random.randrange(1, 5))  # Generate a random manufacturer number 1 through 5.
		match manu_num:  # Based on the randomly generated manufacturer number, generate a random lot number and assign the manufacturer name.
			case 1:
				manu_name = "Astra Zeneca"
				lot_num = random_letters(5) + "-" + random_numbers(2) + "-" + random_numbers(6)
			case 2:
				manu_name = "Novovax"
				lot_num = random_numbers(4) + "-" + random_numbers(4) + "-" + random_letters(3)
			case 3:
				manu_name = "Dynavax"
				lot_num = random_letters(2) + "-" + random_numbers(6) + "-" + random_letters(5)
			case 4:
				manu_name = "Emergent Biosolutions"
				lot_num = random_letters(2) + "-" + random_letters(8) + "-" + random_numbers(4)
			case 5:
				manu_name = "Moderna"
				lot_num = random_numbers(3) + "-" + random_letters(4) + "-" + random_letters(3)
		rand_month = random.randint(1, 12)  # Generate a random expiration month.
		month_end = month_end_dict.get(rand_month)  # From the random month, look up the last day from month_end_dict.
		mydict = {"manufacturer": manu_name, "lotNum": lot_num, "expDate": datetime.datetime(year=2024, month=rand_month, day=random.randint(1, month_end))}  # Generate the vaccine record using all previously generated data.
		result = mycol.insert_one(mydict)  # Add the vaccine record to the database.
		print(result)  # Print the results of the action to the console.

def resetdatabase(int):
	cleardatabase()
	generate_vaccines(int)