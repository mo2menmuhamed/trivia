import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={'/': {'origins': '*'}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')

    return response

  def paginate_questions(request):
    page = request.args.get('page',1,type=int)
    start = (page-1)*QUESTIONS_PER_PAGE
    end = start+QUESTIONS_PER_PAGE
    questions = Question.query.all()
    return questions[start:end]

  def format_data(items):
    formatted_items = [item.format() for item in items]
    return formatted_items

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  
  @app.route('/categories')
  def get_categories():
    categories = Category.query.order_by(Category.type).all()

    if len(categories) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'categories': {category.id: category.type for category in categories}
    }), 200

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions')
  def get_questions():
    questions = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request)
    questions_data = format_data(current_questions)

    categories = Category.query.order_by(Category.type).all()

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': questions_data,
      'total_questions': len(questions),
      'categories': {category.id: category.type for category in categories},
      'current_category': None
    }), 200

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    question = Question.query.filter_by(id=id).one_or_none()

    if not question:
      abort(404)

    question.delete()

    return jsonify({
      'success': True,
      'message': 'Question successfully deleted'
    }), 200

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()

    question = body.get('question')
    answer = body.get('answer')
    difficulty = body.get('difficulty')
    category = body.get('category')

    if ((question is None) or (answer is None) or (difficulty is None) or (category is None)):
      abort(422)
      
    try:
      new_question = Question(question=question, answer=answer, difficulty=difficulty, category=int(category))
      new_question.insert()

      return jsonify({
        'success': True,
        'message': 'Question successfully created!'
      }), 201

    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    body = request.get_json()
    s = body.get('searchTerm')

    if s == '':
      abort(422)

    try:
      search_results = Question.query.filter(
        Question.question.ilike(f'%{s}%')).all()
      
      if len(search_results) == 0:
        abort(404)
      
      return jsonify({
        'success': True,
        'questions': format_data(search_results),
        'total_questions': len(search_results)
      }), 200

    except Exception:
      abort(404)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<int:id>/questions', methods=['GET'])
  def get_questions_by_cat(id):

    category = Category.query.filter_by(id=id).one_or_none()

    if (category is None):
      abort(422)

    try:
      questions = Question.query.filter(Question.category == str(id)).all()

      return jsonify({
        'success': True,
        'questions': [question.format() for question in questions],
        'total_questions': len(questions),
        'current_category': category.type
      }), 200
    except Exception:
      abort(404)

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def play_quiz_question():
    try:
      body = request.get_json()

      category = body.get('quiz_category')
      previous_questions = body.get('previous_questions')

      if((category is None) or (previous_questions is None)):
        abort(422)
      
      if category['type'] == '':
        questions = Question.query.filter(Question.id.notin_((previous_questions))).all()
      else:
        questions = Question.query.filter_by(category=category['id']).filter(Question.id.notin_((previous_questions))).all()

      new = questions[random.randrange(0, len(questions))].format() if len(questions) > 0 else None

      return jsonify({
        'success': True,
        'question': new
      }), 200
    except Exception:
      abort(422)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          'success': False,
          'error': 400,
          'message': 'Bad request error'
      }), 400

  # Error handler for resource not found (404)
  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          'success': False,
          'error': 404,
          'message': 'Resource not found'
      }), 404

  # Error handler for internal server error (500)
  @app.errorhandler(500)
  def internal_server_error(error):
      return jsonify({
          'success': False,
          'error': 500,
          'message': 'An error has occured, please try again'
      }), 500

  # Error handler for unprocesable entity (422)
  @app.errorhandler(422)
  def unprocesable_entity(error):
      return jsonify({
          'success': False,
          'error': 422,
          'message': 'Unprocessable entity'
      }), 422

  
  return app

    