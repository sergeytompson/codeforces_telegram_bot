import peewee
import settings
import logging

db = peewee.PostgresqlDatabase(settings.DB, **settings.DB_CONFIG)

logging.basicConfig(level=logging.INFO, handlers=[
    logging.FileHandler('./logging/codeforces.log', 'w', 'utf-8')
])


class BaseModel(peewee.Model):
    class Meta:
        database = db


class Tag(BaseModel):
    name = peewee.CharField(unique=True)


class Contest(BaseModel):
    pass


class Problem(BaseModel):
    number = peewee.CharField(unique=True)
    name = peewee.CharField()
    link = peewee.CharField()
    rating = peewee.IntegerField()
    solved_count = peewee.CharField()
    contest = peewee.ForeignKeyField(Contest, backref='problems', on_delete='SET NULL', null=True)


class ProblemTags(BaseModel):
    problem = peewee.ForeignKeyField(Problem, on_delete='CASCADE', backref='tags')
    tag = peewee.ForeignKeyField(Tag, on_delete='CASCADE', backref='problems')


class ChatState(BaseModel):
    chat_id = peewee.IntegerField()
    rating = peewee.IntegerField()


db.create_tables([Tag, Contest, Problem, ProblemTags, ChatState, ])
