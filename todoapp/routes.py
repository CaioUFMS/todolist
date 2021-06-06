from flask import render_template, url_for, flash, redirect
from todoapp.forms import FormCadastro, FormLogin, FormBuscaLista, FormLista, FormTarefa
from flask_login import login_user, current_user, logout_user, login_required
from todoapp.models import Usuario, Lista, Tarefa
from todoapp import app, bcrypt


@app.route('/')
@app.route('/home')
@app.route('/sobre')
def sobre():
    return render_template('sobre.html', title='Sobre')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for('listas'))
    form = FormCadastro()
    if form.validate_on_submit():
        hash_senha = bcrypt.generate_password_hash(form.senha.data).decode('utf-8')
        Usuario.create(nome=form.nome.data, email=form.email.data, senha=hash_senha)
        flash(f'Usuário {form.nome.data} foi criado com sucesso!', 'success')
        return redirect(url_for('login'))
    else:
        return render_template('cadastro.html', title='Cadastro', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('lista'))
    form = FormLogin()
    if form.validate_on_submit():
        user = Usuario.get_or_none(Usuario.email == form.email.data)
        if user and bcrypt.check_password_hash(user.senha, form.senha.data):
            login_user(user)
            return redirect(url_for('listas'))
        else:
            flash('Falha no login. Verifique o email e senha inseridos.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/listas', defaults={'id_lista': None}, methods=['GET', 'POST'])
@app.route('/listas/<int:id_lista>', methods=['GET', 'POST'])
@login_required
def listas(id_lista):
    if id_lista:
        lista = Lista.get_or_none(Lista.id == id_lista)
        if not lista or lista.usuario.id != current_user.id:
            flash('Lista não encontrada.', 'info')
            return redirect(url_for('listas'))

    form = FormBuscaLista()
    if form.validate_on_submit():
        if form.nome.data != '':
            listas = Lista.select().where((Lista.nome.startswith(form.nome.data)) & (Lista.usuario == current_user.id))
        else:
            listas = Lista.select().where(Lista.usuario == current_user.id)
    else:
        listas = Lista.select().where(Lista.usuario == current_user.id)
    lista_ativa = Lista.get_or_none(Lista.id == id_lista)
    if not lista_ativa:
        lista_ativa = Lista.get_or_none(Lista.usuario == current_user.id)
        if lista_ativa:
            return redirect(url_for('listas', id_lista=lista_ativa.id))

    return render_template('lista.html', title='Listas', listas=listas, lista_ativa=lista_ativa, form=form)


@app.route('/listas/criar_lista', methods=['GET', 'POST'])
@login_required
def criar_lista():
    lista = Lista.create(nome='Lista de tarefas', descricao='Descrição da lista de tarefas.', usuario=current_user.id)
    return redirect(url_for('listas', id_lista=lista.id))


@app.route('/listas/<int:id_lista>/editar', methods=['GET', 'POST'])
@login_required
def editar_lista(id_lista):
    lista = Lista.get_or_none(Lista.id == id_lista)
    if not lista or lista.usuario.id != current_user.id:
        flash('Lista não encontrada.', 'info')
        return redirect(url_for('listas'))
    form = FormLista()
    if form.validate_on_submit():
        if not lista:
            flash('Esta lista não existe.')
            return redirect(url_for('listas'))
        lista.nome = form.nome.data
        lista.descricao = form.descricao.data
        lista.save()
        flash('Lista alterada com sucesso!', 'success')
        return redirect(url_for('listas', id_lista=lista.id))
    return render_template('editar_lista.html', lista=lista, form=form)


@app.route('/listas/<int:id_lista>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_lista(id_lista):
    lista = Lista.get_or_none(Lista.id == id_lista)
    if not lista or lista.usuario.id != current_user.id:
        flash('Lista não encontrada.', 'info')
        return redirect(url_for('listas'))
    Tarefa.delete().where(Tarefa.lista == id_lista).execute()
    Lista.delete_by_id(id_lista)
    return redirect(url_for('listas'))


@app.route('/listas/<int:id_lista>/tarefas/criar_tarefa', methods=['GET', 'POST'])
@login_required
def criar_tarefa(id_lista):
    lista = Lista.get_or_none(Lista.id == id_lista)
    if not lista or lista.usuario.id != current_user.id:
        flash('Lista não encontrada.', 'info')
        return redirect(url_for('listas'))
    tarefa = Tarefa.create(titulo='Tarefa', descricao='Descrição da tarefa.', lista=id_lista)
    return redirect(url_for('listas', id_lista=id_lista))


@app.route('/listas/<int:id_lista>/tarefas/<int:id_tarefa>/editar', methods=['GET', 'POST'])
@login_required
def editar_tarefa(id_lista, id_tarefa):
    lista = Lista.get_or_none(Lista.id == id_lista)
    if not lista or lista.usuario.id != current_user.id:
        flash('Lista não encontrada.', 'info')
        return redirect(url_for('listas'))
    tarefa = Tarefa.get_or_none(Tarefa.id == id_tarefa)
    if not tarefa:
        flash('Tarefa não encontrada.', 'info')
        return redirect(url_for('listas'))
    form = FormTarefa()
    if form.validate_on_submit():
        if not tarefa:
            flash('Esta tarefa não existe.')
            return redirect(url_for('listas'))
        tarefa.titulo = form.titulo.data
        tarefa.descricao = form.descricao.data
        tarefa.save()
        flash('Tarefa alterada com sucesso!', 'success')
        return redirect(url_for('listas', id_lista=id_lista))
    return render_template('editar_tarefa.html', tarefa=tarefa, form=form, id_lista=id_lista)


@app.route('/listas/<int:id_lista>/tarefas/<int:id_tarefa>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_tarefa(id_lista, id_tarefa):
    lista = Lista.get_or_none(Lista.id == id_lista)
    if not lista or lista.usuario.id != current_user.id:
        flash('Lista não encontrada.', 'info')
        return redirect(url_for('listas'))
    tarefa = Tarefa.get_or_none(Tarefa.id == id_tarefa)
    if not tarefa:
        flash('Tarefa não encontrada.', 'info')
        return redirect(url_for('listas'))
    Tarefa.delete_by_id(id_tarefa)
    return redirect(url_for('listas', id_lista=id_lista))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('sobre'))


if __name__ == '__main__':
    app.run()
