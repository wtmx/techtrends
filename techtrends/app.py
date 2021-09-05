import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
import sys

db_connection_count = 0
post_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    global db_connection_count
    db_connection_count += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Function to check if database connection is made
def check_health():
    try:
        connection = get_db_connection()
        connection.execute('SELECT 1 FROM posts').fetchone()
        return True
    except Exception as e:
        print('Exception: {0}'.format(e))
        return False

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    global post_count
    post_count = len(posts)
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        # log line
        logging.info('Article does not exist!')
        return render_template('404.html'), 404
    else:
        # log line
        logging.info('Existing article "{}" was retrieved!'.format(post['title']))
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    # log line
    logging.info('"About Us" page was retrieved')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            # log line
            logging.info('New article "{}" was created'.format(title))

            return redirect(url_for('index'))

    return render_template('create.html')

# Define the dynamic health status check for the app
@app.route('/healthz')
def healthz():
    if check_health():
        response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
            )
        # log line
        app.logger.info('Status request successful')
    else:
        response = app.response_class(
            response=json.dumps({"result":"ERROR - unhealthy"}),
            status=500,
            mimetype='application/json'
            )
        # log line
        app.logger.info('Status request unsuccessful')
    return response

# Define the metrics check for the app
@app.route('/metrics')
def metrics():
    global db_connection_count
    global post_count
    response = app.response_class(
            response=json.dumps({"db_connection_count": db_connection_count,
            "post_count": post_count}),
            status=200,
            mimetype='application/json'
    )
    # log line
    app.logger.info('Metrics request successful')
    return response

# start the application on port 3111
if __name__ == "__main__":
    # set logger to handle STDOUT and STDERR 
    stdout_handler =  logging.StreamHandler(sys.stdout)
    stderr_handler =  logging.StreamHandler(sys.stderr) 
    handlers = [stderr_handler, stdout_handler]
    
    # format output for app.log file
    format_output = '%(asctime)s: %(levelname)s %(name)s %(message)s'
    logging.basicConfig(format=format_output, level=logging.DEBUG, handlers=handlers)
    
    # logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    app.run(host='0.0.0.0', port='3111')