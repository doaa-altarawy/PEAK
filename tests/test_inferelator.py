"""Test inferelator inference method


"""

from flask.ext.testing import TestCase

from . import app, db


class InferelatorTestCase(TestCase):
    """Test inferelator inference method."""

    def create_app(self):
        app.config.from_object('config.TestConfiguration')
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_users_can_logout(self):
        User.create(name="Joe", email="joe@joes.com", password="12345")

        with self.client:
            self.client.post(url_for("users.login"),
                         data={"email": "joe@joes.com",
                               "password": "12345"})
            self.client.get(url_for("users.logout"))

            self.assertTrue(current_user.is_anonymous())
