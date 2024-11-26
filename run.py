import os
import subprocess
from film_point import create_app

app = create_app()

if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    # Add Flask Debugger directly in this case
    if os.environ.get("FLASK_ENV") == "development":
        command = [
            "watchmedo",
            "auto-restart",
            "--patterns=*.py;*.html;*.css;.env",
            "--recursive",
            "--",
            "flask",
            "run",
            "--host=0.0.0.0",
            "--port=5000",
        ]
        env = dict(os.environ, PYTHONBREAKPOINT="pdb.set_trace")
        subprocess.run(command, env=env)  # subprocess used for auto-reloading
    else:
        # Running Flask directly without watchmedo
        app.run(debug=True, host="0.0.0.0", port=5000)