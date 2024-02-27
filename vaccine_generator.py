import random
import string
import pymongo
import datetime

client = pymongo.MongoClient("mongodb+srv://vaccine_buddy_user:Br4bODkOhkhvcOU0@cluster0.2efzlbn.mongodb.net/?retryWrites=true&w=majority")
mydb = client["vaccine_buddy"]  # Name of the database
mycol = mydb["inventory"]  # Name of the collection

month_end_dict = {
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


def random_letters(length: int) -> string: # Generate a string of random uppercase letters with user defined length
	random_letters_id = ''.join(random.choice(string.ascii_uppercase) for i in range(length))
	return random_letters_id


def random_numbers(length: int) -> string: # Generate a string of random numbers with user defined length
	random_numbers_id = ''.join(random.choice(string.digits) for i in range(length))
	return random_numbers_id


def generate_vaccines(amount: int):
	for i in range(0,amount-1):
		manu_num = round(random.randrange(1,5))
		match manu_num:
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
		rand_month = round(random.randrange(1, 12))
		month_end = month_end_dict.get(rand_month)
		mydict = {"manufacturer": manu_name, "lotNum": lot_num, "expDate": datetime.datetime(year=2024, month=round(random.randrange(1, 12)), day=round(random.randrange(1, month_end)))}
		result = mycol.insert_one(mydict)
		print(result)