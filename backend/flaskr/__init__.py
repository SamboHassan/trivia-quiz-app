import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import json

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        """This set up cors and allow '*' for origins"""

        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    @app.route("/categories")
    def categories():
        """This define a GET endpoint to fetch all available categories"""
        categories = Category.query.order_by(Category.type).all()

        if len(categories) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "categories": {category.id: category.type for category in categories},
            }
        )

    @app.route("/questions")
    def questions():
        """Define a GET requests to all paginated questions"""

        items_limit = request.args.get("limit", QUESTIONS_PER_PAGE, type=int)
        selected_page = request.args.get("page", 1, type=int)
        current_index = selected_page - 1

        question_count = Question.query.count()

        questions = (
            Question.query.order_by(Question.id)
            .limit(items_limit)
            .offset(current_index * items_limit)
            .all()
        )

        if len(questions) == 0:
            abort(404)

        categories = Category.query.order_by(Category.type).all()

        return jsonify(
            {
                "success": True,
                "categories": {category.id: category.type for category in categories},
                "questions": [question.format() for question in questions],
                "total_questions": question_count,
                "selected_page": selected_page,
            }
        )

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        """This define a DELETE endpoint to delete a question using its id"""

        question = Question.query.filter(Question.id == question_id).one_or_none()

        if question:
            question.delete()
            return jsonify({"success": True, "deleted_id": question_id})
        else:
            return json.dumps({"success": False, "error": "Not found"}), 404

    @app.route("/questions", methods=["POST"])
    def create_question():
        """Define a POST endpoint to create a new question"""

        data = dict(request.form or request.json or request.data)

        new_question = Question(
            question=data.get("question"),
            answer=data.get("answer"),
            category=data.get("category"),
            difficulty=data.get("difficulty", 1),
        )

        if (
            not new_question.question
            or not new_question.answer
            or not new_question.category
        ):
            return json.dumps({"success": False, "error": "Missing parameter."}), 400
        else:
            try:
                new_question.insert()
                return (
                    json.dumps({"success": True, "question_id": new_question.id})
                ), 201

            except Exception as e:
                print(e)
                return (
                    json.dumps({"success": False, "error": "An error has occured"})
                ), 500

    @app.route("/questions/search", methods=["POST"])
    def search_question():
        """This define a POST endpoint to get questions based on a search term."""
        data = dict(request.form or request.json or request.data)
        search_term = data.get("searchTerm")

        if search_term:
            questions = Question.query.filter(
                Question.question.ilike(f"%{search_term}%")
            ).all()
            return jsonify(
                {
                    "success": True,
                    "questions": [question.format() for question in questions],
                }
            )
        else:
            return json.dumps({"success": False, "error": "Missing Parameters"}), 400

    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_questions_by_category(category_id):
        """This define a GET endpoint to get question based on category"""
        try:
            questions = Question.query.filter(Question.category == category_id).all()
            return jsonify(
                {
                    "success": True,
                    "questions": [question.format() for question in questions],
                }
            )
        except Exception as e:
            print(e)
            return json.dumps({"success": False, "error": "An error has occurred"}), 500

    @app.route("/quizzes", methods=["POST"])
    def retrieve_quiz_question():
        """This define a POST endpoint to get questions to play the quiz"""

        # data = dict(request.json or request.form or request.data)

        # get_json() converts the JSON object into Python dict
        request_data = request.get_json()
        # print(data)
        previous_questions = request_data.get("previous_questions", [])
        quiz_category = request_data.get("quiz_category")
        # previous_questions = request_data["previous_questions"]
        # quiz_category = request_data["quiz_category"]

        if not quiz_category:
            return json.dumps({"success": False, "error": "Missing params."}), 400
        else:
            if quiz_category["id"] == 0:
                selected_question = (
                    Question.query.filter(Question.id.notin_(previous_questions))
                    .limit(1)
                    .one_or_none()
                )
            else:
                selected_question = (
                    Question.query.filter_by(category=quiz_category["id"])
                    .filter(Question.id.notin_(previous_questions))
                    .limit(1)
                    .one_or_none()  # returns at most one result or raise an exception
                )

            if selected_question:
                return jsonify(
                    {"success": True, "question": selected_question.format()}
                )
            else:
                return (
                    json.dumps({"success": False, "errror": "Question not found."}),
                    404,
                )

    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({"success": False, "error": 400, "message": "Bad request"}), 400

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"success": False, "error": "404", "message": "Not found"}), 404

    @app.errorhandler(422)
    def unprocessable_error(error):
        return (
            jsonify(
                {"success": False, "error": "422", "message": "Unprocessable entity"}
            ),
            422,
        )

    @app.errorhandler(500)
    def unprocessable_error(error):
        return (
            jsonify(
                {"success": False, "error": 500, "message": "Internal Server error"}
            ),
            500,
        )

    return app
