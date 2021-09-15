import sqlite3
import logging
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort


# Define all of the connected databases
database_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global database_count
    database_count = database_count + 1 
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row 
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info('The post with the id {} was not found'.format(post_id))
      return render_template('404.html'), 404
    else:
      app.logger.info('Post {} was accessed'.format(post["title"]))
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info("The About Us page is retrieved")
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
            app.logger.info('A new post {} has been created'.format(title))
            return redirect(url_for('index'))

    return render_template('create.html')

# Define the healthz endpoint for health-checking
@app.route("/healthz")
def healthz():
    try:
        connection = get_db_connection()
        connection.cursor()
        connection.execute("SELECT * FROM posts")
        connection.close()
        return{"result":"OK-healthy"}
    except Exception:
     return{"result":"ERROR-unhealthy"},500

# Define the metrics endpoint for metrics and 
@app.route("/metrics")
def metrics():
        connection = get_db_connection()
        posts = connection.execute("SELECT * FROM posts").fetchone()[0]
        connection.close()
        response = app.response_class(
            response = json.dumps(
                {"db_connection_count": database_count, "post_count": posts
            }
            ),
            status = 200,
            mimetype = 'application/json'
        )
        return response

# def logs(messsage):
#     app.logger.info("{time} | {message}".format(
#         time = datetime.now().strftime("%d/%m/%y,%H:%M:%S"), message=messsage))

# start the application on port 3111
if __name__ == "__main__":
    # Stream the application logs
    formatter = logging.Formatter(
        '%(levelname)s:%(name)s:%(asctime)s, %(message)s', '%d/%m/%Y, %H:%M:%S')
    app.logger.setLevel(logging.DEBUG)

    stdout = logging.StreamHandler(sys.stdout)
    stdout.setFormatter(formatter)
    app.logger.addHandler(stdout)

    stderr = logging.StreamHandler(sys.stderr)
    stderr.setFormatter(formatter)
    app.logger.addHandler(stderr)
    app.run(host='0.0.0.0', port='3111')
