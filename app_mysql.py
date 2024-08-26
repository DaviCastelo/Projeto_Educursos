from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import mysql.connector
from mysql.connector import Error
import sys


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.secret_key = 'seu_chave_secreta'

# Configuração da conexão MySQL
try:
    connection = mysql.connector.connect(
        host='127.0.0.1',
        database='educursos',
        user='root',
        password='Filhotes3'
    )
except Error as e:
    print("Erro ao conectar ao MySQL", e)
    sys.exit(1)

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def user_loader(user_id):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    if result:
        user = User(result['id'], result['username'])
        return user
    return None

def get_curso_info(id_curso, usuario_atual):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cursos WHERE id = %s", (id_curso,))
    curso_info = cursor.fetchone()
    vagas_disponiveis = curso_info['vagas_disponiveis'] if curso_info else 0
    cursor.execute("SELECT * FROM inscricoes_cursos WHERE id_usuario = %s AND id_curso = %s", (usuario_atual, id_curso))
    inscrito = cursor.fetchone() is not None
    cursor.close()
    return curso_info, vagas_disponiveis, inscrito

def get_user_name(user_id):
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
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        user_result = cursor.fetchone()
        if user_result and user_result['password'] == password:
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
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        user_result = cursor.fetchone()
        if user_result:
            flash('Usuário já existe no sistema!', 'error')
        elif password == confirm_password:
            cursor.execute("INSERT INTO usuarios (nome, sobrenome, username, password) VALUES (%s, %s, %s, %s)", (nome, sobrenome, username, password))
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
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT p.*, c.nome AS nome_curso FROM provas p JOIN inscricoes_cursos ic ON p.id_curso = ic.id_curso JOIN cursos c ON c.id = ic.id_curso WHERE ic.id_usuario = %s", (current_user.id,))
    provas = cursor.fetchall()  # Recupera todas as provas do banco de dados

    cursor.close()
    if not provas:
        return render_template('provas.html', title='Provas', active_page='provas', user_name=user_name, message="Você não possui nenhuma prova.")
    else:
        return render_template('provas.html', title='Provas', active_page='provas', user_name=user_name, provas=provas)


@app.route('/trabalhos')
@login_required
def trabalhos():
    user_name = get_user_name(current_user.id)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT t.*, c.nome AS nome_curso FROM trabalhos t JOIN inscricoes_cursos ic ON t.id_curso = ic.id_curso JOIN cursos c ON c.id = ic.id_curso WHERE ic.id_usuario = %s", (current_user.id,))
    trabalhos = cursor.fetchall()  # Recupera todos os trabalhos do banco de dados

    # Busca apenas os cursos em que o usuário está inscrito
    cursor.execute("SELECT c.* FROM cursos c JOIN inscricoes_cursos ic ON c.id = ic.id_curso WHERE ic.id_usuario = %s", (current_user.id,))
    cursos = cursor.fetchall()

    cursor.close()
    if not trabalhos:
        return render_template('trabalhos.html', title='Trabalhos', active_page='trabalhos', user_name=user_name, message="Você não possui nenhum trabalho para fazer.", cursos=cursos)
    else:
        return render_template('trabalhos.html', title='Trabalhos', active_page='trabalhos', user_name=user_name, trabalhos=trabalhos, cursos=cursos)

@app.route('/get_trabalhos')
def get_trabalhos():
    id_curso = request.args.get('curso')
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM trabalhos WHERE id_curso = %s", (id_curso,))
    trabalhos = cursor.fetchall()
    cursor.close()
    return jsonify(trabalhos=trabalhos)

@app.route('/upload_trabalho', methods=['POST'])
@login_required
def upload_trabalho():
 
    if request.method == 'POST':
        
        # id_trabalho = request.form['trabalho']
        # arquivo = request.files['arquivo']

       
        flash('Trabalho enviado com sucesso.', 'success')
        return redirect(url_for('trabalhos'))
    else:
        
        return redirect(url_for('trabalhos'))

@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    user_name = get_user_name(current_user.id)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (current_user.id,))
    user_data = cursor.fetchone()

    # Busca as inscrições do usuário
    cursor.execute("SELECT c.nome FROM inscricoes_cursos ic JOIN cursos c ON ic.id_curso = c.id WHERE ic.id_usuario = %s", (current_user.id,))
    inscricoes = [row['nome'] for row in cursor.fetchall()]

    if request.method == 'POST':
        # Atualiza as informações do usuário no banco de dados
        nome = request.form['nome']
        sobrenome = request.form['sobrenome']
        username = request.form['username']
        password = request.form['password']
        cursor.execute("UPDATE usuarios SET nome = %s, sobrenome = %s, username = %s, password = %s WHERE id = %s", (nome, sobrenome, username, password, current_user.id))
        connection.commit()
        # Recarrega os dados do usuário após a atualização
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (current_user.id,))
        user_data = cursor.fetchone()

    cursor.close()
    return render_template('perfil.html', title='Perfil', active_page='perfil', user_name=user_name, user_data=user_data, inscricoes=inscricoes)

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

# Substitua a rota antiga pela nova rota 'eventos/ciencias_de_dados/inscricao'
@app.route('/cursos/ciencias_de_dados/inscricao', methods=['POST'])
@login_required
def inscricao_ciencias_de_dados():
    id_curso = 1  # ID do curso de Ciências de Dados
    usuario_atual = current_user.id
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inscricoes_cursos WHERE id_usuario = %s AND id_curso = %s", (usuario_atual, id_curso))
    inscricao = cursor.fetchone()
    if inscricao:
        # Se o usuário já estiver inscrito, remova a inscrição e adicione a vaga de volta
        cursor.execute("DELETE FROM inscricoes_cursos WHERE id_usuario = %s AND id_curso = %s", (usuario_atual, id_curso))
        cursor.execute("UPDATE cursos SET vagas_disponiveis = vagas_disponiveis + 1 WHERE id = %s", (id_curso,))
    else:
        # Se o usuário não estiver inscrito, inscreva-o e diminua uma vaga disponível
        cursor.execute("INSERT INTO inscricoes_cursos (id_usuario, id_curso) VALUES (%s, %s)", (usuario_atual, id_curso))
        cursor.execute("UPDATE cursos SET vagas_disponiveis = vagas_disponiveis - 1 WHERE id = %s", (id_curso,))
    connection.commit()
    cursor.close()
    return redirect(url_for('ciencias_de_dados'))



@app.route('/cursos/banco_de_dados/inscricao', methods=['POST'])
@login_required
def inscricao_banco_de_dados():
    # Supondo que o ID do curso de Banco de Dados seja 2
    id_curso = 2
    usuario_atual = current_user.id
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inscricoes_cursos WHERE id_usuario = %s AND id_curso = %s", (usuario_atual, id_curso))
    inscricao = cursor.fetchone()
    if inscricao:
        # Se o usuário já estiver inscrito, remova a inscrição e adicione a vaga de volta
        cursor.execute("DELETE FROM inscricoes_cursos WHERE id_usuario = %s AND id_curso = %s", (usuario_atual, id_curso))
        cursor.execute("UPDATE cursos SET vagas_disponiveis = vagas_disponiveis + 1 WHERE id = %s", (id_curso,))
    else:
        # Se o usuário não estiver inscrito, inscreva-o e diminua uma vaga disponível
        cursor.execute("INSERT INTO inscricoes_cursos (id_usuario, id_curso) VALUES (%s, %s)", (usuario_atual, id_curso))
        cursor.execute("UPDATE cursos SET vagas_disponiveis = vagas_disponiveis - 1 WHERE id = %s", (id_curso,))
    connection.commit()
    cursor.close()
    return redirect(url_for('banco_de_dados'))

@app.route('/cursos/nuvem/inscricao', methods=['POST'])
@login_required
def inscricao_nuvem():
    # Supondo que o ID do curso de Nuvem seja 3
    id_curso = 3
    usuario_atual = current_user.id
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inscricoes_cursos WHERE id_usuario = %s AND id_curso = %s", (usuario_atual, id_curso))
    inscricao = cursor.fetchone()
    if inscricao:
        # Se o usuário já estiver inscrito, remova a inscrição e adicione a vaga de volta
        cursor.execute("DELETE FROM inscricoes_cursos WHERE id_usuario = %s AND id_curso = %s", (usuario_atual, id_curso))
        cursor.execute("UPDATE cursos SET vagas_disponiveis = vagas_disponiveis + 1 WHERE id = %s", (id_curso,))
    else:
        # Se o usuário não estiver inscrito, inscreva-o e diminua uma vaga disponível
        cursor.execute("INSERT INTO inscricoes_cursos (id_usuario, id_curso) VALUES (%s, %s)", (usuario_atual, id_curso))
        cursor.execute("UPDATE cursos SET vagas_disponiveis = vagas_disponiveis - 1 WHERE id = %s", (id_curso,))
    connection.commit()
    cursor.close()
    return redirect(url_for('nuvem'))

@app.route('/cursos/design_de_jogos/inscricao', methods=['POST'])
@login_required
def inscricao_design_de_jogos():
    # Supondo que o ID do curso de Design de Jogos seja 4
    id_curso = 4
    usuario_atual = current_user.id
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inscricoes_cursos WHERE id_usuario = %s AND id_curso = %s", (usuario_atual, id_curso))
    inscricao = cursor.fetchone()
    if inscricao:
        # Se o usuário já estiver inscrito, remova a inscrição e adicione a vaga de volta
        cursor.execute("DELETE FROM inscricoes_cursos WHERE id_usuario = %s AND id_curso = %s", (usuario_atual, id_curso))
        cursor.execute("UPDATE cursos SET vagas_disponiveis = vagas_disponiveis + 1 WHERE id = %s", (id_curso,))
    else:
        # Se o usuário não estiver inscrito, inscreva-o e diminua uma vaga disponível
        cursor.execute("INSERT INTO inscricoes_cursos (id_usuario, id_curso) VALUES (%s, %s)", (usuario_atual, id_curso))
        cursor.execute("UPDATE cursos SET vagas_disponiveis = vagas_disponiveis - 1 WHERE id = %s", (id_curso,))
    connection.commit()
    cursor.close()
    return redirect(url_for('design_de_jogos'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

