import os
import unittest
import json

from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.app.config.from_object("config.TestingConfig")

        # self.database_name = DB_TRIVIA_TEST
        # self.database_path = "postgresql://{}:{}@{}/{}".format(
        #     DB_USER, DB_PASSWORD, DB_HOST, DB_TRIVIA_TEST
        # )
        # setup_db(self.app, self.database_path)

        setup_db(self.app)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_fetch_all_categories(self):
        """Test for fetching all categories."""
        res = self.client().get("/categories")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data.get("categories"))
        self.assertTrue(data.get("success"))

    def test_fetch_all_questions(self):
        """Test for fetching all questions."""
        res = self.client().get("/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data.get("questions"))
        self.assertTrue(data.get("categories"))
        self.assertTrue(data.get("success"))

    def test_get_paginated_questions(self):
        """Test for paginating questions."""
        res = self.client().get("/questions?page=2")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data.get("questions"))
        self.assertTrue(data.get("categories"))
        self.assertTrue(data.get("success"))

    def test_get_limited_questions(self):
        """Test for fetching limited number of questions."""
        res = self.client().get("/questions?limit=1")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data.get("questions"))
        self.assertTrue(len(data.get("questions")), 1)
        self.assertTrue(data.get("categories"))
        self.assertTrue(data.get("success"))

    def test_delete_question(self):
        """Test for deleting a question."""
        # create a dummy question to test deletion
        question = {
            "question": "A dummy question",
            "answer": "A dummy answer",
            "difficulty": 1,
            "category": 1,
        }
        operation_res = self.client().post("/questions", json=question)
        result_data = json.loads(operation_res.data)

        res = self.client().delete(
            "/questions/{}".format(result_data.get("question_id"))
        )

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data.get("deleted_id"), result_data.get("question_id"))
        self.assertTrue(data.get("success"))

    def test_404_if_question_does_not_exist(self):
        """Test the delete endpoint if a question is not found."""
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data.get("success"), False)
        self.assertEqual(data.get("error"), "Not found")

    def test_create_new_question(self):
        question = {
            "question": "A dummy question",
            "answer": "A dummy answer",
            "difficulty": 1,
            "category": 1,
        }

        res = self.client().post("/questions", json=question)
        self.assertEqual(res.status_code, 201)

    def test_400_if_create_question_fail(self):
        question = {"answer": "yyy", "difficulty": 1, "category": 1}

        res = self.client().post("/questions", json=question)
        self.assertEqual(res.status_code, 400)

    def test_get_questions_by_search(self):
        search_term = {"searchTerm": "title"}
        res = self.client().post("/questions/search", json=search_term)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data.get("questions"))

    def test_400_if_get_questions_by_search_fail(self):
        res = self.client().post("/questions/search")
        self.assertEqual(res.status_code, 400)

    def test_get_questions_by_category(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data.get("questions"))

    def test_404_if_get_questions_by_category_fail(self):
        res = self.client().get("/categories/1xx/questions")
        self.assertEqual(res.status_code, 404)

    def test_fetch_quiz_question(self):
        data = {"previous_questions": [], "quiz_category": {"type": "science", "id": 1}}
        res = self.client().post("/quizzes", json=data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data.get("question"))

    def test_400_if_fetch_quiz_question_fail(self):
        data = {"previous_questions": []}
        res = self.client().post("/quizzes", json=data)
        self.assertEqual(res.status_code, 400)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
