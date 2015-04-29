import flask
from app import app
from .forms import LoginForm

@app.route('/')
def main():
  return flask.render_template('main.html', tweets=[{'id': 1, 'text': 'a'}, {'id': 2, 'text': 'b'}])

@app.route('/login', methods=['GET', 'POST'])
def login():
  form = LoginForm()
  if form.validate_on_submit():
    flask.flash('Login requested for OpenID="%s", remember_me=%s' % (form.openid.data, str(form.remember_me.data)))
    return flask.redirect('/')
  return  flask.render_template('login.html', form=form)
