from pathlib import Path

import environ
from django.core.management.base import BaseCommand
from pymongo import MongoClient

from quotes.models import Author, Quote, Tag

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')


class Command(BaseCommand):
    mongo_connection_string = env('MONGO_CONNECTION_STRING')

    author_ids_mapping = {}

    def handle(self, *args, **options):
        mongo_db = self.get_mongo_db()
        self.migrate_authors(mongo_db)
        self.migrate_quotes(mongo_db)

    def get_mongo_db(self):
        client = MongoClient(self.mongo_connection_string)
        db = client.website_quotes

        return db

    def migrate_authors(self, mongo_db):
        authors = list(mongo_db.authors.find())

        for author in authors:
            mongo_author_id = author.pop('_id')
            postgres_author, _ = Author.objects.get_or_create(**author)

            self.author_ids_mapping[str(mongo_author_id)] = postgres_author.id

        self.stdout.write(f'Loaded {len(authors)} authors from mongo.')

    def migrate_quotes(self, mongo_db):
        quotes = list(mongo_db.quotes.find())

        for quote in quotes:
            quote.pop('_id')
            author_id = str(quote.pop('author', ''))
            tag_list = quote.pop('tags', [])

            if author_id:
                quote['author_id'] = self.author_ids_mapping.get(author_id)

            quote, _ = Quote.objects.get_or_create(**quote)
            quote.tags.add(*self._get_tag_instances(tag_list))

        self.stdout.write(f'Loaded {len(quotes)} quotes from mongo.')

    @staticmethod
    def _get_tag_instances(tag_list):
        unique_tags = set([tag.lower() for tag in tag_list])
        quote_tags = []

        for unique_tag in unique_tags:
            tag, _ = Tag.objects.get_or_create(name=unique_tag)
            quote_tags.append(tag)

        return quote_tags
