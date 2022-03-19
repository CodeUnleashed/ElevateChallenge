# Prerequisite

To run this service, you will need to install the following package(s):

- [python 3.10](https://www.python.org/downloads/release/python-3100/) - This is the version of python used to develop this system. Using an older version of python can cause incompatibility issues.
- [requests](https://docs.python-requests.org/en/latest/user/install/) - This is the library we will use to make our HTTP requests to the mock server.
  - You can do this by running `pip install requests`

# System Overview

## Architecture Diagram

![Architecture Diagram](./system%20diagram.drawio.png)

## Components

### Main

This is the entry point into our program. This component will launch the Incidents Server to which clients can connect and request for a summary of the incidents.

### Client

This is a representation of external clients sending requests to our server.

### Data Collector (Thread)

This is a thread which will request the mock server for incidents (every 30 minutes). When it receives a response, it will save/update the Incidents Files.

### Incidents (JSON) File

This is the location to which the Incidents will be saved as JSON objects. This contents of this file will be updated every 30 mins. This is what will be returned to clients requesting incidents. This will be sorted by the employee ID then timestamps of the incidents.

### Data Collector

This is the class which will send the HTTP request to the mock server to retrieve the incidents. This class will send a request to each of the type endpoints then insert the data into a JSON dictionary, then save the dictionary to Incidents File.

## Assumptions

- Only one client will request to connect with our server.
  - If we want to support more clients, we should consider using a queue from which our requests will be read.
- Only one instance of our server will be running at a time.
  - If we have multiple servers running we can consider implementing some sort of load balancing to distribute the load across our servers.

# Setup Instructions

These are the steps you'll need to follow to run the server.

1. Install [Python 3.10](https://www.python.org/downloads/release/python-3100/)
2. Install [requests](https://docs.python-requests.org/en/latest/user/install/)
3. Go in the same directory as [main_server.py](./main_server.py)
4. Run `python main_server.py` to launch the server.
   - This will also start launch the DataCollector Polling Thread
5. Send an HTTP GET Request to localhost:9000.
   - I used [Postman](https://www.postman.com/) for my testing.
   - This will return contents of the Incident File as a JSON.
6. To terminate the server type `ctrl + c`

# Future Improvements

- Add pagination support
  - Currently, we are just returning all the data in the response. Adding support for pagination would allow us to return chunks of data at a time.
- Add unit/integration/end-to-end tests
  - With the given time constraints it wasn't feasible to implement unit/integration/end-to-end tests. This would have made finding bugs a lot quicker and provided us with a safer way to update the system in the future.
  - All testing done on this service was manual using a combination of python and postman.
- Backoff - Currently we are using a 10 second timeout for our requests. If we don't receive a response in 10 seconds the request will fail. We then try again with the next set of requests. Implementing a backoff mechanism would allow us to retry the endpoints after a certain amount of time. This can be beneficial because the request could fail when the client/server experiences a temporary issue.
- Store Username and Password securely. For this project, I stored the username and password as text. This is a VERY BAD idea in production. A proper solution to storing credentials would be to use something like AWS Secrets Manager from which we can autorize our application to retrieve credentials.

# Solutions Considered and Disgarded

These are some of the solutions that were considered and disgarded.

1. AWS API Gateway + AWS Lambda + AWS S3
   - AWS Lambda is serverless way to run code in the cloud. We could have used two AWS Lambda functions one to poll for data and another to process and store the data to a JSON file in S3. Then any client could use the AWS API Gateway to request the processed Incident Data which would be returned by the second AWS Lambda function. This solution would have cost money and was overkill for our usecase.
