from rest_framework import serializers
from django.core.validators import EmailValidator
from datetime import date
from .models import User, Book, Loan


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[EmailValidator()])
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'role')
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate_email(self, value):
        if value and not value.strip():
            raise serializers.ValidationError("Email cannot be empty.")
        return value
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)


class BookSerializer(serializers.ModelSerializer):
    def validate_isbn(self, value):
        """Validate ISBN format - should be 10 or 13 digits"""
        if not value:
            raise serializers.ValidationError("ISBN is required.")
        # Remove hyphens and spaces
        isbn_clean = value.replace('-', '').replace(' ', '')
        if not isbn_clean.isdigit():
            raise serializers.ValidationError("ISBN must contain only digits (and hyphens/spaces).")
        if len(isbn_clean) not in [10, 13]:
            raise serializers.ValidationError("ISBN must be 10 or 13 digits long.")
        return isbn_clean
    
    def validate_page_count(self, value):
        """Validate page_count is positive"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Page count must be a positive number.")
        return value
    
    class Meta:
        model = Book
        fields = ('id', 'title', 'author', 'isbn', 'page_count', 'availability')


class LoanSerializer(serializers.ModelSerializer):
    book_title = serializers.ReadOnlyField(source='book.title')
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    def validate_due_date(self, value):
        """Validate due_date is in the future"""
        if value and value <= date.today():
            raise serializers.ValidationError("Due date must be in the future.")
        return value
    
    class Meta:
        model = Loan
        fields = ('id', 'user', 'book', 'book_title', 'loan_date', 'due_date', 'return_date', 'is_returned')
        read_only_fields = ('loan_date', 'return_date', 'is_returned')
