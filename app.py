from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from supabase_py import create_client, Client

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.secret_key = 'seu_chave_secreta'

url: str = "https://umthiytqwmzawqtzglqt.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVtdGhpeXRxd216YXdxdHpnbHF0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTUzNDI5NDAsImV4cCI6MjAzMDkxODk0MH0.lwVMO5O5NecK3HadQx9OZaSfFsuJ7G-V_49eeMrck84"
supabase: Client = create_client(url, key)

class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
    result = supabase.table("usuarios").select("*").eq('username', username).single()
    if result:
        user = User()
        user.id = username
        return user

# @login_manager.user_loader
# def user_loader(user_id):
#     user_id_str = str(user_id)  # Converte o ID do usuário para string
#     result = supabase.table("usuarios").select("*").eq('id', user_id_str).single().execute()

#     # Verifica se 'data' está presente e contém pelo menos um elemento
#     if result.get('data') and isinstance(result['data'], list) and len(result['data']) > 0:
#         user_data = result['data'][0]
#         user = User()
#         user.id = user_id_str  # O ID do usuário deve ser uma string
#         return user
#     else:
#         # Se 'data' estiver vazia ou não for uma lista, retorne None
#         return None


@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_result = supabase.table("usuarios").select("*").eq('username', username).execute()

        if user_result['data']:  # se o usuário existir
            stored_password = user_result['data'][0]['password']
            if stored_password == password:  # verifique a senha
                user = User()
                user.id = username
                login_user(user)
                return redirect(url_for('home'))
        flash('Usuário ou senha inválidos. Por favor, tente novamente.', 'error')
    return render_template('login.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         user_result = supabase.table("usuarios").select("*").eq('username', username).execute()

#         if user_result['data']:
#             user_data = user_result['data'][0]
#             stored_password = user_data['password']
#             if stored_password == password:
#                 user = User()
#                 user.id = str(user_data['id'])
#                 login_user(user)
#                 flash('Login bem-sucedido! Redirecionando...', 'success')
#                 print(f"Usuário autenticado: {current_user.is_authenticated}")  # Para depuração
#                 print(f"Redirecionando para 'home' com user.id: {user.id}")
#                 return redirect(url_for('home'))
#         flash('Usuário ou senha inválidos. Por favor, tente novamente.', 'error')
#     return render_template('login.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome'].capitalize()
        sobrenome = request.form['sobrenome'].capitalize()
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Verifique se o usuário já existe
        user_result = supabase.table("usuarios").select("*").eq('username', username).execute()
        if user_result['data']:
            flash('Usuário já existe no sistema!', 'error')
            return render_template('register.html')

        if password == confirm_password:
            # Adicione o novo usuário ao banco de dados
            supabase.table("usuarios").insert({
                "nome": nome,
                "sobrenome": sobrenome,
                "username": username,
                "password": password
            }).execute()
            flash('Conta criada com sucesso.', 'success')
            return redirect(url_for('login'))
        else:
            flash('As senhas não coincidem. Por favor, tente novamente.', 'error')
    return render_template('register.html')

@app.errorhandler(401)  # Caso não esteja logado e tente ir para uma página via link direto
def page_not_found(e):  # retorne para a tela de login
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    print(f"Usuário na home: {current_user.is_authenticated}, ID: {current_user.id}")
    return render_template('home.html', title='Página inicial', active_page='home')


@app.route('/eventos')
@login_required
def eventos():
    return render_template('eventos.html', title='Eventos', active_page='eventos')

@app.route('/trabalhos')
@login_required
def trabalhos():
    return render_template('trabalhos.html', title='Trabalhos', active_page='trabalhos')

@app.route('/provas')
@login_required
def provas():
    return render_template('provas.html', title='Provas', active_page='provas')

@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    if request.method == 'POST':
        nome = request.form['nome']
        sobrenome = request.form['sobrenome']
        username = request.form['username']
        password = request.form['password']  # Certifique-se de usar hash na senha

        # Atualiza as informações do usuário no banco de dados
        update_result = supabase.table("usuarios").update({
            "nome": nome,
            "sobrenome": sobrenome,
            "password": password  # A senha deve ser armazenada com hash
        }).eq('username', current_user.id).execute()

        if 'error' not in update_result:
            # Se o nome de usuário foi alterado, atualize o ID do usuário atual
            if current_user.id != username:
                current_user.id = username
            # Redireciona de volta para a página de perfil com as informações atualizadas
            return redirect(url_for('perfil'))

    # Busca as informações do usuário logado para exibir no formulário
    user_info = supabase.table("usuarios").select("*").eq('username', current_user.id).execute()
    if 'data' in user_info and len(user_info['data']) > 0:
        user_data = user_info['data'][0]
        return render_template('perfil.html', user_data=user_data)
    else:
        # Se não encontrar o usuário, redireciona para a página inicial
        return redirect(url_for('home'))



@app.route('/configuracoes')
@login_required
def configuracoes():
    return render_template('configuracoes.html', title='Configuracões', active_page='configuracoes')

# Páginas derivadas
@app.route('/eventos/ciencias_de_dados')
@login_required
def ciencias_de_dados():
    return render_template('ciencias_de_dados.html')

@app.route('/eventos/nuvem')
@login_required
def nuvem():
    return render_template('nuvem.html')

@app.route('/eventos/design_de_jogos')
@login_required
def design_de_jogos():
    return render_template('design_de_jogos.html')

@app.route('/eventos/banco_de_dados')
@login_required
def banco_de_dados():
    return render_template('banco_de_dados.html')

@app.route('/eventos/ciencias_de_dados/inscrever', methods=['POST'])
@login_required
def inscrever_ciencias_de_dados():
    return inscrever_curso(1, 'ciencias_de_dados')  # Supondo que o ID do curso de Ciências de Dados seja 1

@app.route('/eventos/nuvem/inscrever', methods=['POST'])
@login_required
def inscrever_nuvem():
    return inscrever_curso(2, 'nuvem')  # Supondo que o ID do curso de Nuvem seja 2

@app.route('/eventos/design_de_jogos/inscrever', methods=['POST'])
@login_required
def inscrever_design_de_jogos():
    return inscrever_curso(3, 'design_de_jogos')  # Supondo que o ID do curso de Design de Jogos seja 3

@app.route('/eventos/banco_de_dados/inscrever', methods=['POST'])
@login_required
def inscrever_banco_de_dados():
    return inscrever_curso(4, 'banco_de_dados')  # Supondo que o ID do curso de Banco de Dados seja 4

# def inscrever_curso(id_curso, nome_curso):
#     usuario_atual = current_user.id  # Obtém o ID do usuário atual da sessão
#     curso_info = supabase.table("cursos").select("*").eq('id', str(id_curso)).single().execute()

#     if curso_info.get('data'):
#         curso_data = curso_info['data']
#         vagas_disponiveis = curso_data.get('vagas_disponiveis')
#         if vagas_disponiveis is not None and vagas_disponiveis > 0:
#             # Insere a inscrição do usuário no banco de dados
#             inscricao = supabase.table("inscricoes_cursos").insert({
#                 "id_usuario": usuario_atual,
#                 "id_curso": id_curso
#             }).execute()

#             # Verifica se a inserção foi bem-sucedida
#             if inscricao.get('data'):
#                 # Atualiza o número de vagas disponíveis
#                 supabase.table("cursos").update({
#                     "vagas_disponiveis": vagas_disponiveis - 1
#                 }).eq('id', str(id_curso)).execute()

#                 flash('Inscrição realizada com sucesso!', 'success')
#             else:
#                 flash('Não foi possível realizar a inscrição.', 'error')
#         else:
#             flash('Não há vagas disponíveis.', 'error')
#     else:
#         flash('Informações do curso não encontradas ou incompletas.', 'error')

#     # Retorna para a mesma página do curso com a mensagem de flash
#     return render_template(f'{nome_curso}.html', title='Inscrição para curso')

def inscrever_curso(id_curso, nome_curso):
    usuario_atual = current_user.id  # Obtém o ID do usuário atual da sessão
    curso_info = supabase.table("cursos").select("*").eq('id', str(id_curso)).single().execute()

    if 'error' not in curso_info:
        print(f"Conexão bem-sucedida para o curso {nome_curso}.")
        curso_data = curso_info.get('data')
        vagas_disponiveis = curso_data.get('vagas_disponiveis')
        if vagas_disponiveis is not None and vagas_disponiveis > 0:
            # Insere a inscrição do usuário no banco de dados
            inscricao = supabase.table("inscricoes_cursos").insert({
                "id_usuario": usuario_atual,
                "id_curso": id_curso
            }).execute()

            if 'error' not in inscricao:
                print(f"Inscrição bem-sucedida para o usuário {usuario_atual}.")
                # Atualiza o número de vagas disponíveis
                atualizacao = supabase.table("cursos").update({
                    "vagas_disponiveis": vagas_disponiveis - 1
                }).eq('id', str(id_curso)).execute()

                return redirect(url_for(f'{nome_curso}'))

                # if 'error' not in atualizacao:
                #     flash('Inscrição realizada com sucesso!', 'success')
                # else:
                #     print(f"Erro ao atualizar as vagas disponíveis: {atualizacao.get('error')}")
                #     flash('Erro ao atualizar as vagas disponíveis.', 'error')
            else:
                print(f"Erro na inscrição: {inscricao.get('error')}")
                # flash('Não foi possível realizar a inscrição.', 'error')
        # else:
        #     flash('Não há vagas disponíveis.', 'error')
    else:
        print(f"Erro na conexão: {curso_info.get('error')}")
        flash('Informações do curso não encontradas ou incompletas.', 'error')

    return render_template(f'{nome_curso}.html', title='Inscrição para curso')




# @app.route('/welcome')
# @login_required
# def welcome():
#     return 'Bem-vindo! Você está logado.'

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
