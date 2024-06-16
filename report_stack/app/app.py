from flask import Flask, request
from pymongo import MongoClient
import re

app = Flask(__name__)

username = 'root'
password = 'example'
host = 'mongodb'
port = 27017
connection_string = f'mongodb://{username}:{password}@{host}:{port}/'

client = MongoClient(connection_string)
db = client['mac_records']
collection = db['records']




def format_mac(mac: str) -> str:
    """ Convert any MAC format to uniform xx:xx:xx:xx:xx:xx format """
    mac = re.sub('[.:-]', '', mac).lower()  # remove delimiters and convert to lower case
    mac = ''.join(mac.split())  # remove whitespaces
    assert len(mac) == 12  # length should be now exactly 12 (eg. 008041aefd7e)
    assert mac.isalnum()  # should only contain letters and numbers
    # convert mac in canonical form (eg. 00:80:41:ae:fd:7e)
    mac = ":".join(["%s" % (mac[i:i+2]) for i in range(0, 12, 2)])
    return mac


def lower_case_keys(dictionary):
    """
    :param dictionary: A dictionary object.
    :return: A dictionary with all keys converted to lowercase.

    This method takes a dictionary and recursively converts all keys to lowercase. If the input dictionary is nested, the method will also recursively convert keys of nested dictionaries and lists to lowercase. If a non-dictionary or non-list object is encountered, it will be returned as is.

    Example usage:

    >>> my_dictionary = {'Name': 'John', 'Age': 30, 'Address': {'City': 'New York', 'State': 'NY'}}
    >>> lower_case_keys(my_dictionary)
    {'name': 'John', 'age': 30, 'address': {'city': 'New York', 'state': 'NY'}}
    """
    if isinstance(dictionary, dict):
        return {k.lower(): lower_case_keys(v) for k, v in dictionary.items()}
    elif isinstance(dictionary, list):
        return [lower_case_keys(item) for item in dictionary]
    else:
        return dictionary


@app.route('/add_mac_record', methods=['POST'])
def add_mac_record():
    try:
        data = lower_case_keys(request.json)
        buffer = []

        for record in data['data']:
            # we want only dynamic records
            if 'DYNAMIC' in record['type']:
                # add hostname
                record['hostname'] = data['hostname']
                # uniform mac address
                record['destination_address'] = format_mac(record['destination_address'])
                buffer.append(record)

        # push our buffer to mongo
        for dataset in buffer:
            if collection.count_documents(dataset) == 0:
                collection.insert_one(dataset)
            else:
                # update create
                pass

        return {'message': 'Record added successfully'}, 200
    except Exception as e:
        return {'message': str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=True)