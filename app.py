
from flask import Flask, request, render_template, redirect, flash, session, make_response
from surveys import surveys
from flask_debugtoolbar import DebugToolbarExtension

KEY = "responses"
CURRENT_SURVEY_KEY = 'current_survey'

app = Flask(__name__)
app.config['SECRET_KEY'] = "oh-so-secret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

@app.route('/home')
def pick_survey():
   
    return render_template('pick-survey.html', surveys = surveys)

@app.route('/start', methods=["POST"])
def start_survey():
    picked_survey = request.form['picks']
    # prevents re-taking a survey until cookie times out:
    if request.cookies.get(f"completed_{picked_survey}"):
        return render_template("already-done.html")

#   instructions = picked_survey.instructions
    survey = surveys[picked_survey]
    session[CURRENT_SURVEY_KEY] = picked_survey

    return render_template('start-survey.html', survey = survey) #, instructions = instructions)

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
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]
    
    if (responses is None):
        # trying to access question page too soon
        return redirect("/home")

    if (len(responses) == len(survey.questions)):
        # They've answered all the questions! Thank them
        return redirect("/complete")
    # To prevent manual entry of quiestion/id out of order
    if (len(responses) != id):
        
        flash(f'''Invalid question id: {id}.''')
        return redirect(f"/questions/{len(responses)}")

    question = survey.questions[id]
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

    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]
    
    if (len(responses) == len(survey.questions)):
        # They've answered all the questions! Thank them.
        return redirect("/complete")

    else:
        return redirect(f"/questions/{len(responses)}")

@app.route("/complete")
def complete():
    """Survey complete. Show completion page."""
    picked_survey = session[CURRENT_SURVEY_KEY]
    survey = surveys[picked_survey]

    html = render_template("thankyou.html", survey = survey)
# Set cookie noting this survey is done so they can't re-do it:
    response = make_response(html)
    response.set_cookie(f"completed_{picked_survey}", "yes", max_age=120)
    return response

