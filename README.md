# Description
This project is a music streaming web application, allowing user to listen to music, explore new tracks and manage their own playlists.

# How to run
1. Clone the repository

    ```
    git clone git@github.com:gdimitrovdev/Deenie.git
    ```
    or
    ```
    git clone https://github.com/gdimitrovdev/Deenie.git
    ```

2. Create a virtual environment

    ```
    python -m venv venv
    ```

3. Activate the virtual environment
    
    Windows:
    ```
    .\venv\Scripts\activate
    ```
    Linux/Mac:
    ```
    source ./venv/bin/activate
    ```

4. Install the requirements

    ```
    pip install -r requirements.txt
    ```

5. Setup environmental variables
    - Copy the .env.sample file into a new .env file and fill out the missing Spotipy API variables.
    - If you want to use a custom PostgreSQL database instead of an in-memory one, change the DEBUG environmental variable to False and set the database environmental variables as well.

6. Run migrations

    ```
    python manage.py migrate
    ```

7. Run the project

    ```
    python manage.py runserver
    ```

# How to use
Open localhost:8000 or 127.0.0.1:8000 in your browser. If you want to use a different port, you need to run this instead:

    ```
    python manage.py runserver <desired_port>
    ```
