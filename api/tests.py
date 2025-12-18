from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User, Book, Loan
from .serializers import UserSerializer, BookSerializer, LoanSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class UserViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.admin = User.objects.create_superuser(username='admin', password='adminpassword')
        
        refresh = RefreshToken.for_user(self.user)
        self.user_token = str(refresh.access_token)
        
        refresh = RefreshToken.for_user(self.admin)
        self.admin_token = str(refresh.access_token)

    def test_registration(self):
        url = reverse('api:user-list')
        data = {
            'username': 'newuser',
            'password': 'newpassword',
            'email': 'new@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(User.objects.get(username='newuser').username, 'newuser')

    def test_get_users_as_admin(self):
        url = reverse('api:user-list')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_users_as_user(self):
        url = reverse('api:user-list')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_user_as_admin(self):
        url = reverse('api:user-list')
        data = {
            'username': 'newuser',
            'password': 'newpassword',
            'email': 'new@example.com'
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(User.objects.get(username='newuser').username, 'newuser')

    def test_update_user_as_admin(self):
        url = reverse('api:user-detail', kwargs={'pk': self.user.pk})
        data = {
            'username': 'updateduser'
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')

    def test_delete_user_as_admin(self):
        url = reverse('api:user-detail', kwargs={'pk': self.user.pk})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 1)


class BookViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.admin = User.objects.create_superuser(username='admin', password='adminpassword')
        
        refresh = RefreshToken.for_user(self.user)
        self.user_token = str(refresh.access_token)
        
        refresh = RefreshToken.for_user(self.admin)
        self.admin_token = str(refresh.access_token)
        
        self.book1 = Book.objects.create(
            title='Test Book 1',
            author='Author 1',
            isbn='1234567890123',
            page_count=100,
            availability=True
        )
        self.book2 = Book.objects.create(
            title='Test Book 2',
            author='Author 2',
            isbn='9876543210987',
            page_count=200,
            availability=False
        )

    def test_anonymous_user_can_list_books(self):
        url = reverse('api:book-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_anonymous_user_cannot_create_book(self):
        url = reverse('api:book-list')
        data = {
            'title': 'New Book',
            'author': 'New Author',
            'isbn': '1111111111111',
            'page_count': 150
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_cannot_create_book(self):
        url = reverse('api:book-list')
        data = {
            'title': 'New Book',
            'author': 'New Author',
            'isbn': '1111111111111',
            'page_count': 150
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_book(self):
        url = reverse('api:book-list')
        data = {
            'title': 'New Book',
            'author': 'New Author',
            'isbn': '1111111111111',
            'page_count': 150
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 3)

    def test_admin_can_update_book(self):
        url = reverse('api:book-detail', kwargs={'pk': self.book1.pk})
        data = {'title': 'Updated Title'}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, 'Updated Title')

    def test_admin_can_delete_book(self):
        url = reverse('api:book-detail', kwargs={'pk': self.book1.pk})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 1)

    def test_filter_by_availability(self):
        url = reverse('api:book-list')
        response = self.client.get(url, {'availability': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertTrue(response.data['results'][0]['availability'])

    def test_search_by_title(self):
        url = reverse('api:book-list')
        response = self.client.get(url, {'search': 'Book 1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Book 1')

    def test_search_by_author(self):
        url = reverse('api:book-list')
        response = self.client.get(url, {'search': 'Author 2'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['author'], 'Author 2')

    def test_pagination(self):
        # Create more books to test pagination
        for i in range(15):
            Book.objects.create(
                title=f'Book {i}',
                author=f'Author {i}',
                isbn=f'111111111111{i}',
                page_count=100
            )
        url = reverse('api:book-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)  # PAGE_SIZE is 10
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)

    def test_invalid_data_handling(self):
        url = reverse('api:book-list')
        data = {
            'title': '',  # Empty title
            'author': 'Author',
            'isbn': '123',
            'page_count': -10  # Negative page count
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoanViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.user2 = User.objects.create_user(username='testuser2', password='testpassword2')
        self.admin = User.objects.create_superuser(username='admin', password='adminpassword')
        
        refresh = RefreshToken.for_user(self.user)
        self.user_token = str(refresh.access_token)
        
        refresh = RefreshToken.for_user(self.user2)
        self.user2_token = str(refresh.access_token)
        
        refresh = RefreshToken.for_user(self.admin)
        self.admin_token = str(refresh.access_token)
        
        self.book1 = Book.objects.create(
            title='Available Book',
            author='Author 1',
            isbn='1234567890123',
            page_count=100,
            availability=True
        )
        self.book2 = Book.objects.create(
            title='Unavailable Book',
            author='Author 2',
            isbn='9876543210987',
            page_count=200,
            availability=False
        )

    def test_user_can_create_loan(self):
        url = reverse('api:loan-list')
        data = {
            'book': self.book1.id,
            'due_date': (date.today() + timedelta(days=14)).isoformat()
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Loan.objects.count(), 1)
        self.book1.refresh_from_db()
        self.assertFalse(self.book1.availability)

    def test_book_availability_set_to_false_when_borrowed(self):
        url = reverse('api:loan-list')
        data = {
            'book': self.book1.id,
            'due_date': (date.today() + timedelta(days=14)).isoformat()
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)
        self.assertTrue(self.book1.availability)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.book1.refresh_from_db()
        self.assertFalse(self.book1.availability)

    def test_user_cannot_borrow_unavailable_book(self):
        url = reverse('api:loan-list')
        data = {
            'book': self.book2.id,
            'due_date': (date.today() + timedelta(days=14)).isoformat()
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('not available', str(response.data))

    def test_user_can_only_see_own_loans(self):
        loan1 = Loan.objects.create(
            user=self.user,
            book=self.book1,
            due_date=date.today() + timedelta(days=14),
            is_returned=False
        )
        loan2 = Loan.objects.create(
            user=self.user2,
            book=self.book2,
            due_date=date.today() + timedelta(days=14),
            is_returned=False
        )
        url = reverse('api:loan-list')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], loan1.id)

    def test_admin_can_see_all_loans(self):
        loan1 = Loan.objects.create(
            user=self.user,
            book=self.book1,
            due_date=date.today() + timedelta(days=14)
        )
        loan2 = Loan.objects.create(
            user=self.user2,
            book=self.book2,
            due_date=date.today() + timedelta(days=14)
        )
        url = reverse('api:loan-list')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_return_book_sets_availability_to_true(self):
        loan = Loan.objects.create(
            user=self.user,
            book=self.book1,
            due_date=date.today() + timedelta(days=14)
        )
        self.book1.availability = False
        self.book1.save()
        
        url = reverse('api:loan-return-book', kwargs={'pk': loan.pk})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertTrue(self.book1.availability)

    def test_return_book_marks_loan_as_returned(self):
        loan = Loan.objects.create(
            user=self.user,
            book=self.book1,
            due_date=date.today() + timedelta(days=14)
        )
        url = reverse('api:loan-return-book', kwargs={'pk': loan.pk})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        loan.refresh_from_db()
        self.assertTrue(loan.is_returned)
        self.assertIsNotNone(loan.return_date)
        self.assertEqual(loan.return_date, date.today())

    def test_user_cannot_return_another_users_loan(self):
        loan = Loan.objects.create(
            user=self.user2,
            book=self.book1,
            due_date=date.today() + timedelta(days=14)
        )
        url = reverse('api:loan-return-book', kwargs={'pk': loan.pk})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_due_date_is_required(self):
        url = reverse('api:loan-list')
        data = {
            'book': self.book1.id
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserModelTest(TestCase):
    def test_user_creation_with_default_role(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        self.assertEqual(user.role, 'user')
        self.assertFalse(user.is_staff)

    def test_user_role_choices(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        user.role = 'admin'
        user.save()
        self.assertEqual(user.role, 'admin')


class BookModelTest(TestCase):
    def test_book_creation(self):
        book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890123',
            page_count=100
        )
        self.assertEqual(book.title, 'Test Book')
        self.assertEqual(book.author, 'Test Author')
        self.assertEqual(book.isbn, '1234567890123')
        self.assertEqual(book.page_count, 100)

    def test_book_default_availability(self):
        book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890123',
            page_count=100
        )
        self.assertTrue(book.availability)

    def test_isbn_uniqueness(self):
        Book.objects.create(
            title='Book 1',
            author='Author',
            isbn='1234567890123',
            page_count=100
        )
        with self.assertRaises(Exception):  # IntegrityError
            Book.objects.create(
                title='Book 2',
                author='Author',
                isbn='1234567890123',
                page_count=200
            )

    def test_book_string_representation(self):
        book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890123',
            page_count=100
        )
        self.assertEqual(str(book), 'Test Book')


class LoanModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890123',
            page_count=100
        )

    def test_loan_creation(self):
        loan = Loan.objects.create(
            user=self.user,
            book=self.book,
            due_date=date.today() + timedelta(days=14)
        )
        self.assertEqual(loan.user, self.user)
        self.assertEqual(loan.book, self.book)
        self.assertIsNotNone(loan.loan_date)

    def test_loan_date_auto_now_add(self):
        before = date.today()
        loan = Loan.objects.create(
            user=self.user,
            book=self.book,
            due_date=date.today() + timedelta(days=14)
        )
        after = date.today()
        self.assertGreaterEqual(loan.loan_date, before)
        self.assertLessEqual(loan.loan_date, after)

    def test_loan_string_representation(self):
        loan = Loan.objects.create(
            user=self.user,
            book=self.book,
            due_date=date.today() + timedelta(days=14)
        )
        self.assertEqual(str(loan), f'{self.user.username} - {self.book.title}')

    def test_loan_foreign_key_relationships(self):
        loan = Loan.objects.create(
            user=self.user,
            book=self.book,
            due_date=date.today() + timedelta(days=14)
        )
        self.assertEqual(loan.user, self.user)
        self.assertEqual(loan.book, self.book)


class UserSerializerTest(TestCase):
    def test_serialization_includes_all_fields(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        serializer = UserSerializer(user)
        data = serializer.data
        self.assertIn('id', data)
        self.assertIn('username', data)
        self.assertIn('email', data)
        self.assertIn('role', data)


class BookSerializerTest(TestCase):
    def test_serialization(self):
        book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890123',
            page_count=100,
            availability=True
        )
        serializer = BookSerializer(book)
        data = serializer.data
        self.assertEqual(data['title'], 'Test Book')
        self.assertEqual(data['author'], 'Test Author')
        self.assertEqual(data['isbn'], '1234567890123')
        self.assertEqual(data['page_count'], 100)
        self.assertEqual(data['availability'], True)

    def test_deserialization(self):
        data = {
            'title': 'New Book',
            'author': 'New Author',
            'isbn': '1111111111111',
            'page_count': 150,
            'availability': True
        }
        serializer = BookSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        book = serializer.save()
        self.assertEqual(book.title, 'New Book')
        self.assertEqual(book.isbn, '1111111111111')


class LoanSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890123',
            page_count=100
        )

    def test_book_title_is_read_only(self):
        loan = Loan.objects.create(
            user=self.user,
            book=self.book,
            due_date=date.today() + timedelta(days=14)
        )
        serializer = LoanSerializer(loan)
        data = serializer.data
        self.assertIn('book_title', data)
        self.assertEqual(data['book_title'], 'Test Book')

    def test_serialization_includes_all_fields(self):
        loan = Loan.objects.create(
            user=self.user,
            book=self.book,
            due_date=date.today() + timedelta(days=14)
        )
        serializer = LoanSerializer(loan)
        data = serializer.data
        self.assertIn('id', data)
        self.assertIn('user', data)
        self.assertIn('book', data)
        self.assertIn('book_title', data)
        self.assertIn('loan_date', data)
        self.assertIn('due_date', data)


class LoanWorkflowTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')
        
        refresh = RefreshToken.for_user(self.user1)
        self.user1_token = str(refresh.access_token)
        
        refresh = RefreshToken.for_user(self.user2)
        self.user2_token = str(refresh.access_token)
        
        self.book1 = Book.objects.create(
            title='Book 1',
            author='Author 1',
            isbn='1111111111111',
            page_count=100,
            availability=True
        )
        self.book2 = Book.objects.create(
            title='Book 2',
            author='Author 2',
            isbn='2222222222222',
            page_count=200,
            availability=True
        )

    def test_complete_borrow_workflow(self):
        # User borrows book
        url = reverse('api:loan-list')
        data = {
            'book': self.book1.id,
            'due_date': (date.today() + timedelta(days=14)).isoformat()
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user1_token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify book is unavailable
        self.book1.refresh_from_db()
        self.assertFalse(self.book1.availability)
        
        # Verify loan exists
        self.assertEqual(Loan.objects.count(), 1)
        loan = Loan.objects.first()
        self.assertEqual(loan.user, self.user1)
        self.assertEqual(loan.book, self.book1)
        
        # Return book
        return_url = reverse('api:loan-return-book', kwargs={'pk': loan.pk})
        response = self.client.post(return_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify book is available again
        self.book1.refresh_from_db()
        self.assertTrue(self.book1.availability)
        
        # Verify loan is marked as returned (not deleted)
        loan.refresh_from_db()
        self.assertTrue(loan.is_returned)
        self.assertIsNotNone(loan.return_date)
        self.assertEqual(Loan.objects.count(), 1)

    def test_multiple_users_borrowing_different_books(self):
        # User1 borrows book1
        url = reverse('api:loan-list')
        data1 = {
            'book': self.book1.id,
            'due_date': (date.today() + timedelta(days=14)).isoformat()
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user1_token)
        response = self.client.post(url, data1, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # User2 borrows book2
        data2 = {
            'book': self.book2.id,
            'due_date': (date.today() + timedelta(days=14)).isoformat()
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user2_token)
        response = self.client.post(url, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify both books are unavailable
        self.book1.refresh_from_db()
        self.book2.refresh_from_db()
        self.assertFalse(self.book1.availability)
        self.assertFalse(self.book2.availability)
        
        # Verify both loans exist
        self.assertEqual(Loan.objects.count(), 2)

    def test_user_cannot_borrow_same_book_twice(self):
        # User1 borrows book1
        url = reverse('api:loan-list')
        data = {
            'book': self.book1.id,
            'due_date': (date.today() + timedelta(days=14)).isoformat()
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user1_token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Try to borrow same book again
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('not available', str(response.data))

    def test_pagination_in_book_list_after_borrowing(self):
        # Create multiple books
        books = []
        for i in range(12):
            book = Book.objects.create(
                title=f'Book {i}',
                author=f'Author {i}',
                isbn=f'999999999900{i}',
                page_count=100,
                availability=True
            )
            books.append(book)
        
        # Borrow one book
        url = reverse('api:loan-list')
        data = {
            'book': books[0].id,
            'due_date': (date.today() + timedelta(days=14)).isoformat()
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user1_token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check book list pagination
        book_url = reverse('api:book-list')
        response = self.client.get(book_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)  # PAGE_SIZE is 10
        self.assertIn('next', response.data)
