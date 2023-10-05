from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class Book(models.Model):
    """
    The Book model
    """

    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=50, unique=True)
    author = fields.CharField(max_length=50, null=True)
    description = fields.CharField(max_length=50, null=True)
    new_date = fields.DateField(null=True, auto_now=True)


# Book
Book_Pydantic = pydantic_model_creator(Book, name="Book")
BookIn_Pydantic = pydantic_model_creator(Book, name="BookIn", exclude_readonly=True)
