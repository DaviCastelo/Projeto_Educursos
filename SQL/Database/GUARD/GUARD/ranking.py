import requests
import pandas as pd


base_url = "https://api.hinova.com.br/api/sga/v2"

def listar_veiculos(token_acesso):
    if not token_acesso:
        return None
    
    
    url_veiculos = f"{base_url}/listar/veiculo"

    
    payload = {
        "inicio_paginacao": 0,
        "quantidade_por_pagina": 999,
        "data_cadastro": "2024-05-01",
        "data_cadastro_final": "2024-05-31",
    }

    
    headers_veiculos = {
        "Authorization": f"Bearer {token_acesso}",
        "Content-Type": "application/json"
    }
    
    try:
        
        response = requests.post(url_veiculos, json=payload, headers=headers_veiculos)
        
        if response.status_code == 200:
            veiculos = response.json()
            return veiculos.get("veiculos", [])
        else:
            print(f"Erro ao obter veículos: {response.status_code}, {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Erro na conexão: {e}")
        return []

def criar_ranking_vendas(veiculos):
    if not veiculos:
        return None
    
    
    df_veiculos = pd.DataFrame(veiculos)
    
    
    ranking = df_veiculos.groupby('nome_voluntario')['codigo_veiculo'].count().reset_index()
    
    
    ranking.columns = ['nome_voluntario', 'total_vendas']
    
    
    ranking = ranking.sort_values(by='total_vendas', ascending=False).reset_index(drop=True)
    
    return ranking

def gerar_html_ranking(ranking_vendas):
    if ranking_vendas is None:
        return
    
    
    ranking_html = ranking_vendas.to_html(index=False)

    
    html_content = f'''
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ranking de Vendas - Maio 2024</title>
        <style>
            table {{
                width: 80%;
                border-collapse: collapse;
                margin: 20px auto;
            }}
            th, td {{
                border: 1px solid black;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            .search-box {{
                margin-bottom: 20px;
            }}
        </style>
        <script>
            function searchByName() {{
                var input, filter, table, tr, td, i, txtValue;
                input = document.getElementById("searchInput");
                filter = input.value.toUpperCase();
                table = document.getElementById("rankingTable");
                tr = table.getElementsByTagName("tr");
                
                // Loop through all table rows, starting from index 1 to skip header row
                for (i = 1; i < tr.length; i++) {{
                    td = tr[i].getElementsByTagName("td")[0]; // Index 0 is the first column (nome_voluntario)
                    if (td) {{
                        txtValue = td.textContent || td.innerText;
                        if (txtValue.toUpperCase().indexOf(filter) > -1) {{
                            tr[i].style.display = "";
                        }} else {{
                            tr[i].style.display = "none";
                        }}
                    }}
                }}
            }}

            document.addEventListener("DOMContentLoaded", function() {{
                // Inicialmente, mostrar todas as linhas da tabela
                var table = document.getElementById("rankingTable");
                var rows = table.getElementsByTagName("tr");
                for (var i = 0; i < rows.length; i++) {{
                    rows[i].style.display = "";
                }}

                // Adicionar evento para filtrar em tempo real ao digitar
                var input = document.getElementById("searchInput");
                input.addEventListener("keyup", function() {{
                    searchByName();
                }});
            }});
        </script>
    </head>
    <body>
        <h1>Ranking de Vendas - Maio 2024</h1>
        <div class="search-box">
            <label for="searchInput">Pesquisar por nome do vendedor:</label>
            <input type="text" id="searchInput" placeholder="Digite o nome do vendedor...">
        </div>
        <table id="rankingTable">
            <thead>
                <tr>
                    <th>Nome do Vendedor</th>
                    <th>Total de Vendas</th>
                </tr>
            </thead>
            <tbody>
                {ranking_html}
            </tbody>
        </table>
    </body>
    </html>
    '''

    
    with open('ranking_vendas_maio_2024.html', 'w', encoding='utf-8') as file:
        file.write(html_content)

def main():
   
    try:
        with open("token_sessao.txt", "r") as token_file:
            token_acesso = token_file.read().strip()
    except FileNotFoundError:
        print("Arquivo de token não encontrado. Execute primeiro o script de autenticação.")
        return
    
    
    veiculos = listar_veiculos(token_acesso)
    
    if veiculos:
        
        ranking_vendas = criar_ranking_vendas(veiculos)
        
        
        gerar_html_ranking(ranking_vendas)
        
        print("Arquivo 'ranking_vendas_maio_2024.html' gerado com sucesso.")
    else:
        print("Não foi possível obter os veículos.")


if __name__ == "__main__":
    main()
