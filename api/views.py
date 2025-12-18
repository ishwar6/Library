from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny
from django.db import transaction
from datetime import date
from .models import User, Book, Loan
from .serializers import UserSerializer, BookSerializer, LoanSerializer
from django_filters.rest_framework import DjangoFilterBackend

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminUser]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by('id')
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['availability']
    search_fields = ['title', 'author']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all().order_by('id')
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Loan.objects.all()
        return Loan.objects.filter(user=user, is_returned=False)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        book_id = request.data.get('book')
        if not book_id:
            raise ValidationError({"book": "This field is required."})
        
        try:
            book = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            raise NotFound(f"Book with id {book_id} does not exist.")
        
        if not book.availability:
            raise ValidationError({"book": "This book is not available."})
        
        # Serializer validates due_date format and future date, then saves
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Use transaction to ensure atomicity
        with transaction.atomic():
            book.availability = False
            book.save()
            serializer.save(user=request.user)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        loan = self.get_object()  # Raises NotFound if loan doesn't exist
        
        # Check permission: user can only return their own loans (unless admin)
        if not request.user.is_staff and loan.user != request.user:
            raise ValidationError({"detail": "You can only return your own loans."})
        
        # Check if already returned
        if loan.is_returned:
            raise ValidationError({"detail": "This loan has already been returned."})
        
        # Use transaction to ensure atomicity
        with transaction.atomic():
            loan.book.availability = True
            loan.book.save()
            loan.return_date = date.today()
            loan.is_returned = True
            loan.save()
        
        return Response(status=status.HTTP_200_OK, data={"message": "Book returned successfully."})

