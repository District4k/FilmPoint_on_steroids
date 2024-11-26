import subprocess
from film_point import create_app

app = create_app()

if __name__ == '__main__':
    # Set Flask in debug mode
    app.config['DEBUG'] = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True  # Optional: Ensures template changes trigger reloads.

    # Command to run watchmedo with flask
    command = [
        "watchmedo",
        "auto-restart",
        "--patterns='*.py;*.html;*.css;.env'",
        "--recursive",
        "--",
        "flask",
        "run",
        "--host=0.0.0.0",
    ]

    # Run the command using subprocess
    subprocess.run(command)
