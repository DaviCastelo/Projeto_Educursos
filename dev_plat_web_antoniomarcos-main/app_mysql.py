from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.secret_key = 'seu_chave_secreta'

# Configuração da conexão MySQL
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='devplatweb',
            user='root',
            password='Filhotes3'
        )
        return connection
    except Error as e:
        print("Erro ao conectar ao MySQL", e)
        return None

connection = get_db_connection()

@app.teardown_appcontext
def close_connection(exception):
    if connection and connection.is_connected():
        connection.close()

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def user_loader(user_id):
    connection = get_db_connection()
    if connection is None:
        return None
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    if result:
        user = User(result['id'], result['username'])
        cursor.close()
        return user
    cursor.close()
    return None

def get_curso_info(id_curso, usuario_atual):
    connection = get_db_connection()
    if connection is None:
        return None, 0, False
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cursos WHERE id = %s", (id_curso,))
    curso_info = cursor.fetchone()
    vagas_disponiveis = curso_info['vagas_disponiveis'] if curso_info else 0
    cursor.execute("SELECT * FROM inscricoes_cursos WHERE id_usuario = %s AND id_curso = %s", (usuario_atual, id_curso))
    inscrito = cursor.fetchone() is not None
    cursor.close()
    return curso_info, vagas_disponiveis, inscrito

def get_user_name(user_id):
    connection = get_db_connection()
    if connection is None:
        return 'Usuário'
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT nome FROM usuarios WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    return user_data['nome'] if user_data else 'Usuário'

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        if connection is None:
            flash('Erro ao conectar ao banco de dados.', 'error')
            return render_template('login.html')
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        user_result = cursor.fetchone()
        if user_result and check_password_hash(user_result['password'], password):
            user = User(user_result['id'], user_result['username'])
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Usuário ou senha inválidos. Por favor, tente novamente.', 'error')
        cursor.close()
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome'].capitalize()
        sobrenome = request.form['sobrenome'].capitalize()
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        connection = get_db_connection()
        if connection is None:
            flash('Erro ao conectar ao banco de dados.', 'error')
            return render_template('register.html')
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        user_result = cursor.fetchone()
        if user_result:
            flash('Usuário já existe no sistema!', 'error')
        elif password == confirm_password:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            cursor.execute("INSERT INTO usuarios (nome, sobrenome, username, password) VALUES (%s, %s, %s, %s)", (nome, sobrenome, username, hashed_password))
            connection.commit()
            flash('Conta criada com sucesso.', 'success')
            return redirect(url_for('login'))
        else:
            flash('As senhas não coincidem. Por favor, tente novamente.', 'error')
        cursor.close()
    return render_template('register.html')

@app.errorhandler(401)
def unauthorized(e):
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    user_name = get_user_name(current_user.id)
    return render_template('home.html', title='Página inicial', active_page='home', user_name=user_name)

@app.route('/cursos')
@login_required
def cursos():
    user_name = get_user_name(current_user.id)
    return render_template('cursos.html', title='Cursos', active_page='cursos', user_name=user_name)

@app.route('/provas')
@login_required
def provas():
    user_name = get_user_name(current_user.id)
    return render_template('provas.html', title='Provas', active_page='provas', user_name=user_name)

@app.route('/trabalhos')
@login_required
def trabalhos():
    user_name = get_user_name(current_user.id)
    return render_template('trabalhos.html', title='Trabalhos', active_page='trabalhos', user_name=user_name)

@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    user_name = get_user_name(current_user.id)
    connection = get_db_connection()
    if connection is None:
        flash('Erro ao conectar ao banco de dados.', 'error')
        return render_template('perfil.html')
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (current_user.id,))
    user_data = cursor.fetchone()
    cursor.close()
    return render_template('perfil.html', title='Perfil', active_page='perfil', user_name=user_name, user_data=user_data)

@app.route('/configuracoes')
@login_required
def configuracoes():
    user_name = get_user_name(current_user.id)
    return render_template('configuracoes.html', title='Configurações', active_page='configuracoes', user_name=user_name)

@app.route('/cursos/ciencias_de_dados')
@login_required
def ciencias_de_dados():
    user_name = get_user_name(current_user.id)
    id_curso = 1  # ID do curso de Ciências de Dados
    usuario_atual = current_user.id
    curso_info, vagas_disponiveis, inscrito = get_curso_info(id_curso, usuario_atual)
    return render_template('ciencias_de_dados.html', title='Ciências de Dados', active_page='ciencias_de_dados', user_name=user_name, curso_info=curso_info, vagas_disponiveis=vagas_disponiveis, inscrito=inscrito)

@app.route('/cursos/banco_de_dados')
@login_required
def banco_de_dados():
    user_name = get_user_name(current_user.id)
    curso_info, vagas_disponiveis, inscrito = get_curso_info(2, current_user.id)
    return render_template('banco_de_dados.html', title='Banco de dados', active_page='banco_de_dados', user_name=user_name, curso_info=curso_info, vagas_disponiveis=vagas_disponiveis, inscrito=inscrito)

@app.route('/cursos/nuvem')
@login_required
def nuvem():
    user_name = get_user_name(current_user.id)
    curso_info, vagas_disponiveis, inscrito = get_curso_info(3, current_user.id)
    return render_template('nuvem.html', title='Nuvem', active_page='nuvem', user_name=user_name, curso_info=curso_info, vagas_disponiveis=vagas_disponiveis, inscrito=inscrito)

@app.route('/cursos/design_de_jogos')
@login_required
def design_de_jogos():
    user_name = get_user_name(current_user.id)
    curso_info, vagas_disponiveis, inscrito = get_curso_info(4, current_user.id)
    return render_template('design_de_jogos.html', title='Design de jogos', active_page='design_de_jogos', user_name=user_name, curso_info=curso_info, vagas_disponiveis=vagas_disponiveis, inscrito=inscrito)

@app.route('/cursos/ciencias_de_dados/inscricao', methods=['POST'])
@login_required
def inscricao_ciencias_de_dados():
    id_curso = 1  # ID do curso de Ciências de Dados
    usuario_atual = current_user.id
    connection = get_db_connection()
    if connection is None:
        flash('Erro ao conectar ao banco de dados.', 'error')
        return redirect(url_for('ciencias_de_dados'))
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inscricoes_cursos WHERE id_usuario = %s AND id_curso = %s", (usuario_atual, id_curso))
    inscricao = cursor.fetchone()
    if inscricao:
        cursor.execute("DELETE FROM inscricoes_cursos WHERE id_usuario = %s AND id_curso = %s", (usuario_atual, id_curso))
        cursor.execute("UPDATE cursos SET vagas_disponiveis = vagas_disponiveis + 1 WHERE id = %s", (id_curso,))
    else:
        cursor.execute("INSERT INTO inscricoes_cursos (id_usuario, id_curso) VALUES (%s, %s)", (usuario_atual, id_curso))
        cursor.execute("UPDATE cursos SET vagas_disponiveis = vagas_disponiveis - 1 WHERE id = %s", (id_curso,))
    connection.commit()
    cursor.close()
    return redirect(url_for('ciencias_de_dados'))

@app.route('/cursos/banco_de_dados/inscricao', methods=['POST'])
@login_required
def inscricao_banco_de_dados():
    id_curso = 2
    usuario_atual = current_user.id
    connection = get_db_connection()
    if connection is None:
        flash('Erro ao conectar ao banco de dados.', 'error')
        return redirect(url_for('banco_de_dados'))
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inscricoes_cursos WHERE id_usuario = %s AND id_curso = %s", (usuario_atual, id_curso))
    inscricao = cursor.fetchone()
    if inscricao:
        cursor.execute("DELETE FROM inscricoes_cursos WHERE id_usuario = %s AND id_curso = %s", (usuario_atual, id_curso))
        cursor.execute("UPDATE cursos SET vagas_disponiveis = vagas_disponiveis + 1 WHERE id = %s", (id_curso,))
    else:
        cursor.execute("INSERT INTO inscricoes_cursos (id_usuario, id_curso) VALUES (%s, %s)", (usuario_atual, id_curso))
        cursor.execute("UPDATE cursos SET vagas_disponiveis = vagas_disponiveis - 1 WHERE id = %s", (id_curso,))
    connection.commit()
    cursor.close()
    return redirect(url_for('banco_de_dados'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
