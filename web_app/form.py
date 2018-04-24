from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired


class Start_Form(Form):
    start_data = StringField('start_data', validators=[DataRequired()])  #起始的url或者用户名及其相关词