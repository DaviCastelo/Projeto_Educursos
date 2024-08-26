import requests


base_url = "https://api.hinova.com.br/api/sga/v2"


url_autenticacao = f"{base_url}/usuario/autenticar"


usuario = "tecnologia"
senha = "Evogard2306"
token_fixo = "7274cafe2bb35c4a177cf3aef0650ad50764c3238ae6581dde56d0cfed946744f84f0ada1ff4e4e7bd9dc495cdac16fb8fcfd2dddeed4660269e77d3be4e556f6be6e833073fc506d3b357d45befc103c97140dd72a1c13099e1d438f4e88515"


headers_autenticacao = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token_fixo}"
}

def autenticar_usuario(usuario, senha):
    payload = {
        "usuario": usuario,
        "senha": senha
    }
    
    try:
        
        response = requests.post(url_autenticacao, json=payload, headers=headers_autenticacao)
        
        if response.status_code == 200:
            
            data = response.json()
            print(data)
            token_acesso = data.get("token_usuario")
            return token_acesso
        else:
            print(f"Erro na autenticação: {response.status_code}, {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro na conexão: {e}")
        return None

def main():
    
    token_acesso = autenticar_usuario(usuario, senha)
    
    if token_acesso:
        print("Usuário autenticado com sucesso.")
        
        with open("token_sessao.txt", "w") as token_file:
            token_file.write(token_acesso)
    else:
        print("Falha na autenticação. Verifique as credenciais e tente novamente.")


if __name__ == "__main__":
    main()
