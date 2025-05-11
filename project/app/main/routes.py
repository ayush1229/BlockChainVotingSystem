from flask import Blueprint, render_template, request

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
def index():
    return render_template('index.html', title='Home')

@main.route('/about')
def about():
    return render_template('about.html', title='About')

@main.route('/candidates')
def candidates():
    return render_template('candidates.html', title='Candidates')

@main.route('/importance')
def importance():
    return render_template('importance.html', title='Importance of Voting')

@main.route('/voter')
def voter():
    return render_template('voter.html', title='voter')