import logging
from flask import Flask, render_template
app = Flask(__name__)


@app.route('osu-capstone.herokuapp.com')
def renderIndex():
	return render_template('index.html')

@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500

if __name__ == "__main__":
    app.run()