# inventory_page

1. Using screen:
screen is a terminal multiplexer that allows you to run multiple terminal sessions within a single window. You can start your Flask application within a screen session, detach from the session, and then log out without stopping the application.

Here's how to use screen:

Open a terminal on your Linux server.

Navigate to the directory containing your Flask application (app.py).

Start a new screen session:

Copy code:
``screen -S flask_app``
Within the screen session, run your Flask application:

Copy code
python app.py
To detach from the screen session, press `Ctrl + A` followed by `Ctrl + D`. This will leave the session running in the background.

You can now log out or close the terminal window without stopping the Flask application.

To reattach to the screen session and view the output of your Flask application, use the following command:

Copy code
``screen -r flask_app``
