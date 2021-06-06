from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from todoapp.models import Usuario


class FormCadastro(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    email = StringField('Email',
                        validators=[DataRequired(), Email(message='Email inválido')])
    senha = PasswordField('Senha', validators=[DataRequired()])
    confirma_senha = PasswordField('Confirma senha', validators=[DataRequired(), EqualTo('senha', message='Este campo '
                                                                                                          'deve ser '
                                                                                                          'igual à '
                                                                                                          'senha')])
    submit = SubmitField('Cadastrar')

    def validate_email(self, email):
        usuario = Usuario.get_or_none(Usuario.email == email.data)
        if usuario:
            raise ValidationError('Email já cadastrado. Por favor, utilize outro.')


class FormLogin(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(message='Email inválido')])
    senha = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Login')


class FormLista(FlaskForm):
    nome = StringField('Nome da lista', validators=[DataRequired()])
    descricao = TextAreaField('Descrição da lista', validators=[DataRequired()])
    submit = SubmitField('Alterar lista')


class FormTarefa(FlaskForm):
    titulo = StringField('Título da tarefa', validators=[DataRequired()])
    descricao = TextAreaField('Descrição da tarefa', validators=[DataRequired(), Length(min=20, max=100,
                                                                                        message='A quantidade de '
                                                                                                'caracteres deve ser '
                                                                                                'maior que 20 e menor '
                                                                                                'que 100')])
    data = DateField('Data')
    submit = SubmitField('Alterar tarefa')


class FormBuscaLista(FlaskForm):
    nome = StringField('Nome da lista')
    submit = SubmitField('Buscar')
