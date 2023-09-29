from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class Users(models.Model):
    """
    The User model
    """

    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=20, unique=True)
    full_name = fields.CharField(max_length=50, null=True)
    email = fields.CharField(max_length=50, null=True)
    hashed_password = fields.CharField(max_length=128, null=True)
    # scopes = fields.ManyToManyField("models.Scope", related_name="users")
    scopes = fields.CharField(max_length=128, null=True)
    disabled = fields.BooleanField(default=False)

    class PydanticMeta:
        exclude = ["password_hash"]


# User
User_Pydantic = pydantic_model_creator(Users, name="User")
UserIn_Pydantic = pydantic_model_creator(Users, name="UserIn", exclude_readonly=True)

# class Scope(models.Model):
#     """
#     The Scope model
#     """

#     id = fields.IntField(pk=True)
#     name = fields.CharField(max_length=20, unique=True)
#     description = fields.CharField(max_length=50, null=True)

#     def __str__(self):
#         return self.name


# # Scope
# Scope_Pydantic = pydantic_model_creator(Scope, name="Scope")
# ScopeIn_Pydantic = pydantic_model_creator(Scope, name="ScopeIn", exclude_readonly=True)
