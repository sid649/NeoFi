Hi, I have tried my best to complete the assignment as per your recommendations. I hope you like it :)

I have used postman to test all the api's.

1. Base URL -  http://127.0.0.1:8000/api/ (Run the django development server)

2. To register a new user, use this api - http://127.0.0.1:8000/api/register/
    Required Fields - username, first_name, last_name, email, password

3. To login a user, use this api - http://127.0.0.1:8000/api/login/
    Required Fields - username, password
    Output - auth Token

4. To get the online users, use this api - http://127.0.0.1:8000/api/get-online-users/
    NOTE: Authorization token will be required. (Can use the auth token received in login functionality)

5. To start a chat with other user, use this api - http://127.0.0.1:8000/api/chat/start/
    NOTE: Authorization token will be required.
    Requried Fields - message, receiver

6. To send message from one user to another with django channels, use this api - http://127.0.0.1:8000/api/chat/send/
    Requried Fields - message, receiver

7. To get the recommendations on interests for suggested friends, use this api - http://127.0.0.1:8000/api/suggested-friends/<user-id>/