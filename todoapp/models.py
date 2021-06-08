from peewee import *
from playhouse.shortcuts import model_to_dict
from todoapp import login_manager
from flask_login import UserMixin

db = SqliteDatabase('todoapp/app.db')


@login_manager.user_loader
def load_user(id_usuario):
    return Usuario.get_or_none(Usuario.id == int(id_usuario))


class BaseModel(Model):
    class Meta:
        database = db

    def as_dict(self):
        return model_to_dict(self, recurse=False)


class Usuario(BaseModel, UserMixin):
    id = AutoField()
    nome = CharField()
    email = CharField(unique=True)
    senha = CharField()


class Lista(BaseModel):
    id = AutoField()
    nome = CharField()
    descricao = TextField()
    usuario = ForeignKeyField(Usuario, backref='listas')

    @property
    def porcentagem_conclusao(self):
        tarefas = Tarefa.select().where(Tarefa.lista == self.id)
        concluidas, total = 0, 0
        for tarefa in tarefas:
            if tarefa.concluida:
                concluidas += 1
            total += 1

        return 0 if total == 0 else (concluidas / total) * 100


class Tarefa(BaseModel):
    id = AutoField()
    titulo = CharField()
    descricao = TextField()
    concluida = BooleanField(default=False)
    cor = CharField(default="rgb(255, 255, 255)")
    lista = ForeignKeyField(Lista, backref='tarefas')
