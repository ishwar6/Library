import requests
from django.core.management.base import BaseCommand
from api.models import Book

class Command(BaseCommand):
    help = 'Populates the database with books from the Google Books API.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--query',
            type=str,
            default='subject:fiction',
            help='Search query for Google Books API (default: subject:fiction)'
        )
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of books to fetch (default: 50)'
        )

    def handle(self, *args, **options):
        query = options['query']
        target_count = options['count']
        
        self.stdout.write(f'Fetching books from Google Books API with query: "{query}"')
        
        books_added = 0
        books_skipped_no_isbn = 0
        books_skipped_exists = 0
        
        # Use multiple search queries to get diverse books with ISBNs
        search_queries = [
            f'{query}+inpublisher:penguin',
            f'{query}+inpublisher:harper',
            f'{query}+inpublisher:random+house',
            f'{query}+inpublisher:simon',
            f'{query}+intitle:novel',
            f'{query}+intitle:story',
        ]
        
        for search_query in search_queries:
            if books_added >= target_count:
                break
                
            for start_index in range(0, 40, 10):  # Fetch in smaller batches
                if books_added >= target_count:
                    break
                    
                url = f'https://www.googleapis.com/books/v1/volumes?q={search_query}&maxResults=10&startIndex={start_index}&printType=books&langRestrict=en'
                
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code != 200:
                        self.stderr.write(f'Failed to fetch books: {response.status_code}')
                        continue

                    data = response.json()
                    items = data.get('items', [])
                    
                    if not items:
                        continue

                    for item in items:
                        if books_added >= target_count:
                            break
                            
                        volume_info = item.get('volumeInfo', {})
                        title = volume_info.get('title', 'No Title')
                        authors = volume_info.get('authors', ['Unknown Author'])
                        author = ', '.join(authors)
                        page_count = volume_info.get('pageCount', 0)
                        
                        # Skip books with no page count (often not real books)
                        if page_count == 0:
                            continue
                        
                        # Get ISBN - prefer ISBN_13, fall back to ISBN_10
                        isbn = None
                        industry_identifiers = volume_info.get('industryIdentifiers', [])
                        
                        for identifier in industry_identifiers:
                            if identifier.get('type') == 'ISBN_13':
                                isbn = identifier.get('identifier')
                                break
                        
                        # Fall back to ISBN_10 if no ISBN_13
                        if not isbn:
                            for identifier in industry_identifiers:
                                if identifier.get('type') == 'ISBN_10':
                                    isbn = identifier.get('identifier')
                                    break
                        
                        if not isbn:
                            books_skipped_no_isbn += 1
                            continue

                        # Check if book with this ISBN already exists
                        if Book.objects.filter(isbn=isbn).exists():
                            books_skipped_exists += 1
                            continue

                        book = Book(
                            title=title[:200],  # Truncate to fit model field
                            author=author[:200],
                            isbn=isbn,
                            page_count=page_count,
                            availability=True
                        )
                        book.save()
                        books_added += 1
                        self.stdout.write(f'  Added: {title[:50]}...' if len(title) > 50 else f'  Added: {title}')
                        
                except requests.RequestException as e:
                    self.stderr.write(f'Request error: {e}')
                    continue

        self.stdout.write('')
        self.stdout.write(f'Books added: {books_added}')
        self.stdout.write(f'Books skipped (no ISBN): {books_skipped_no_isbn}')
        self.stdout.write(f'Books skipped (already exists): {books_skipped_exists}')
        self.stdout.write(self.style.SUCCESS('Done!'))
