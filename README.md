# inventory_page

## Using screen
screen is a terminal multiplexer that allows you to run multiple terminal sessions within a single window. You can start your Flask application within a screen session, detach from the session, and then log out without stopping the application.

Here's how to use screen:

1. Open a terminal on your Linux server.
2. Navigate to the directory containing your Flask application (app.py).
3. Start a new screen session:``screen -S flask_app``
4. Within the screen session, run your Flask application: ``python app.py``
5. To detach from the screen session, press `Ctrl + A` followed by `Ctrl + D`. This will leave the session running in the background.
6. You can now log out or close the terminal window without stopping the Flask application.
7. To reattach to the screen session and view the output of your Flask application, use the following command: ``screen -r flask_app``
