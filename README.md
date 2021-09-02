# python-mongo-auth-server
<!-- GETTING STARTED -->
<!-- ABOUT THE PROJECT -->
## About The Project
This is a auth server implementing refresh token rotation algorithm 

### Built With
.
* Python
* MongoDB
* MailJet for mailing

### Installation

1. Pipenv install dependencies
2. Create a MongoDB instance
3. Create a Mailjet token
4. Create a .env file in root directory
5. Define APP_SECRET_KEY and VERIFICATION_CODE_LENGTH at your preference in .env
6. Define MONGO_URI in .env
7. Define MAILJET_KEY and MAILJET_SECRET in .env


<!-- USAGE EXAMPLES -->
## Usage

Create .env and add all those variables mentioned and just run wsgi.py and the server is up

