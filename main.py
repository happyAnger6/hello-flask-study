__author__ = 'zhangxa'

from flask import Flask, request, redirect, make_response, json, url_for, session
from config import DevConfig
from flask_sqlalchemy import SQLAlchemy

from jinja2.utils import generate_lorem_ipsum

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

import os

app = Flask(__name__)
app.config.from_object(DevConfig)
db = SQLAlchemy(app)
app.secret_key = os.getenv('SECRET_KEY', 'secret string')

@app.cli.command()
def hello():
    pass

@app.route('/more')
def post_more():
    return generate_lorem_ipsum(n=1)

@app.route('/post')
def show_post():
    post_body = generate_lorem_ipsum(n=2)
    return '''
<h1> a very long post</h1>
<div class="body">%s</div>
<button id="load">Load More</button>
<script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
<script type="text/javascript">
$(function() {
    $('#load').click(function(){
        $.ajax({
            url: '/more',
            type: 'get',
            success: function(data) {
                $('body').append(data);
            }
         })
    })
})
</script>
    '''  % post_body

@app.route('/hello')
def hello():
    name = request.args.get('name')
    if name is None:
        name = request.cookies.get('name', 'Human')
    response = '<h1>Hello, %s!</h1>' % name
    if 'logged_in' in session:
        response += '[Authenticated]'
    else:
        response += '[Not Authenticated]'
    return response

@app.route('/goback/<int:year>')
def go_back(year):
    return '<p>Welcome to %d!</p>' % (2018 - year)


@app.route('/colors/<any(blue, white, read):color>')
def three_colors(color):
    return '<p>Love is patient and kind. Love is not jealous or boastful or pround or rude [%s].</p>' % str(color)[1:]

@app.route('/redirect')
def redrect():
    return redirect('https://www.baidu.com')

@app.route('/login')
def login():
    session['logged_in'] = True
    return redirect(url_for('hello'))

@app.route('/foo')
def foo():
    data = {
        'name': 'zhangxa',
        'gender': 'male'
    }
    response = make_response(json.dumps(data))
    response.mime_type = 'application/json'
    return response

@app.route('/bar')
def bar():
    return '<h1>Bar page</h1><a href="%s">Do something</a>' % url_for('do_something', next=request.full_path)

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc

def redirect_back(default='hello', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))

@app.route('/do_something')
def do_something():
    #return redirect(request.referrer or url_for('hello'))
    return redirect_back()

@app.route('/set/<name>')
def set_cookie(name):
    response = make_response(redirect(url_for('hello')))
    response.set_cookie('name', name)
    return response

def go_back(year):
    return '<p>Welcome to %d!</p>' % (2018 - year)

class User(db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))

    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return "<User `{}`>".format(self.username)

if __name__ == "__main__":
    app.run()

