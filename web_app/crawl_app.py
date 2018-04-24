from flask import Flask,request,render_template
from graduation_project.web_app.form import Start_Form
from graduation_project.web_app.redis_queue import Queue
app = Flask(__name__)
app.secret_key='renjian'
queue=Queue()

# @app.route('/')
# def index():
#     return render_template('start_crawl.htm')



@app.route('/hello')
def hello():
    return 'Hello World'


# @app.route('/login', methods=['POST', 'GET'])
# def login():
#     error = None
#     if request.method == 'POST':
#         if valid_login(request.form['username'],
#                        request.form['password']):
#             return log_the_user_in(request.form['username'])
#         else:
#             error = 'Invalid username/password'
#     # the code below is executed if the request method
#     # was GET or the credentials were invalid
#     return render_template('login.html', error=error)


@app.route('/', methods=['GET', 'POST'])
def login():
    form = Start_Form()
    if form.validate_on_submit():
        start_data=form.data['start_data']
        if form.data['start_data']:
            queue.push(start_data)
            return 'sucess,your data is %s'%start_data
        else:
            return 'not data'
    return render_template('start_crawl.htm', form=form)



@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return 'User %s' % username


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         do_the_login()
#     else:
#         show_the_login_form()



if __name__ == '__main__':
    app.run(debug=True)