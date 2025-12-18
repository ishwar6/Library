from django.contrib import admin
from .models import User, Book, Loan


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'page_count', 'availability')
    list_filter = ('availability',)
    search_fields = ('title', 'author', 'isbn')
    readonly_fields = ()
    fieldsets = (
        (None, {'fields': ('title', 'author', 'isbn')}),
        ('Details', {'fields': ('page_count', 'availability')}),
    )


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'loan_date', 'due_date', 'return_date', 'is_returned')
    list_filter = ('loan_date', 'due_date', 'is_returned', 'return_date')
    search_fields = ('user__username', 'book__title', 'book__author')
    readonly_fields = ('loan_date',)
    fieldsets = (
        (None, {'fields': ('user', 'book')}),
        ('Dates', {'fields': ('loan_date', 'due_date', 'return_date')}),
        ('Status', {'fields': ('is_returned',)}),
    )
