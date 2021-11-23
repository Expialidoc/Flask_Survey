
from flask import Flask, request, render_template, redirect, flash, session
from surveys import satisfaction_survey
from flask_debugtoolbar import DebugToolbarExtension

KEY = "responses"

app = Flask(__name__)
app.config['SECRET_KEY'] = "oh-so-secret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

#question_list = list()

@app.route('/home')
def start_survey():
    title = satisfaction_survey.title
    instructions = satisfaction_survey.instructions
    
    return render_template('start_survey.html', title = title, instructions = instructions)

@app.route('/begin', methods=["POST"])
def begin():
    session[KEY] = []

    return redirect("/questions/0")

# @app.route('/questions')
# def display_questions():

#     for q in range(0, len(satisfaction_survey.questions)):
#         question_list.append(satisfaction_survey.questions[q].question)

#     return render_template('questions.html', question_list=question_list)
@app.route("/questions/<int:id>")
def show_question(id):
    responses = session.get(KEY)
    if (responses is None):
        # trying to access question page too soon
        return redirect("/home")

    if (len(responses) == len(satisfaction_survey.questions)):
        # They've answered all the questions! Thank them
        return redirect("/complete")
    # To prevent manual entry of quiestion/id out of order
    if (len(responses) != id):
        
        flash(f'''Invalid question id: {id}.''')
        return redirect(f"/questions/{len(responses)}")

    question = satisfaction_survey.questions[id]
    return render_template("questions.html",  question=question) #question_num=id,

@app.route("/answer", methods=["POST"])
def handle_question():
    """Save response and redirect to next question."""

    # get the response choice
    choice = request.form['answer'] # from the form name = "answer"
    # add this response to the session
    responses = session[KEY]
    responses.append(choice)
    session[KEY] = responses

    if (len(responses) == len(satisfaction_survey.questions)):
        # They've answered all the questions! Thank them.
        return redirect("/complete")

    else:
        return redirect(f"/questions/{len(responses)}")

@app.route("/complete")
def complete():
    """Survey complete. Show completion page."""

    return render_template("thankyou.html")

