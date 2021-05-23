try:
    from app import app
    import unittest
except Exception as e:
    print("Some Modules are Missing {} ".format(e))

class FLASKTEST(unittest.TestCase):

    """
    Unit Test
    """

    # 1.Check for response 200 which means that flask loaded correctly
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # 2.Ensure that the login page loads correctly
    def test_login_page_loads(self):
        tester = app.test_client(self)
        response = tester.get('/')
        self.assertIn(b'Login', response.data)

    # 3.Ensure login behaves correctly with correct credentials
    def test_correct_admin_login(self):
        tester = app.test_client()
        response = tester.post(
            '/',
            data=dict(username="admin", password="admin"),
            follow_redirects=True
        )
        self.assertIn(b'Bookings', response.data)

    # 4.Ensure login behaves correctly with incorrect credentials
    def test_incorrect_login(self):
        tester = app.test_client()
        response = tester.post(
            '/',
            data=dict(username="wrong", password="wrong"),
            follow_redirects=True
        )
        self.assertIn(b'Login', response.data)

    # 5.Ensure that main page requires user login
    def test_profile_route_requires_login(self):
        tester = app.test_client()
        response = tester.get('/profile', follow_redirects=True)
        response = tester.get('/', follow_redirects=True)

    # 6.Ensure register behaves correctly with already existing username
    def test_correct_register_existing_username(self):
        tester = app.test_client()
        response = tester.post(
            '/register',
            data=dict(username="test1", firstName ="test1" , lastName= "test1", email= "test2@test1.com", password="test1", confirmPassword="test1"),
            follow_redirects=True
        )
        self.assertIn(b'Account already exists', response.data)

    # 7.Ensure cars loads correctly
    def test_correct_cars(self):
        tester = app.test_client()
        response = tester.post(
            '/',
            data=dict(username="red", password="red"),
            follow_redirects=True
        )
        response = tester.get('/rent', follow_redirects=True)
        self.assertIn(b'Holden', response.data)

    # 8.Ensure Profile loads correctly
    def test_correct_profile(self):
        tester = app.test_client()
        response = tester.post(
            '/',
            data=dict(username="red", password="red"),
            follow_redirects=True
        )
        response = tester.get('/profile', follow_redirects=True)
        self.assertIn(b'User Profile', response.data)

    # 9.Ensure that Edit user loads correctly for Admin
    def test_correct_edituser_page(self):
        tester = app.test_client()
        response = tester.post(
            '/',
            data=dict(username="admin", password="admin"),
            follow_redirects=True
        )
        response = tester.get('/edituser', follow_redirects=True)
        self.assertIn(b'Edit User', response.data)

    # 10.Ensure Edit car loads correctly for Admin
    def test_correct_carmanage_page(self):
        tester = app.test_client()
        response = tester.post(
            '/',
            data=dict(username="admin", password="admin"),
            follow_redirects=True
        )
        response = tester.get('/carmanage', follow_redirects=True)
        self.assertIn(b'Add Car', response.data)
    
    # 11.Ensure Logout works correctly for Admin
    def test_correct_logout(self):
        tester = app.test_client()
        response = tester.post(
            '/',
            data=dict(username="admin", password="admin"),
            follow_redirects=True
        )
        response = tester.get('/logout', follow_redirects=True)
        self.assertIn(b'Login', response.data)
    



    
if __name__ == "__main__":
    unittest.main()