from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('Creating full-text search indexes...')
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS app_question_search_idx 
                    ON app_question 
                    USING GIN(to_tsvector('english', title || ' ' || content))
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS app_question_title_search_idx 
                    ON app_question 
                    USING GIN(to_tsvector('english', title))
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS app_question_content_search_idx 
                    ON app_question 
                    USING GIN(to_tsvector('english', content))
                """)
                
                self.stdout.write(
                    self.style.SUCCESS('Successfully created full-text search indexes')
                )
                
        except Exception as e:
            if 'does not exist' in str(e):
                self.stdout.write(
                    self.style.WARNING('Not using PostgreSQL - full-text indexes not created')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Error creating indexes: {e}')
                ) 