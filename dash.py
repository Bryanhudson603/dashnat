import streamlit as st
import pandas as pd
import re

def extrair_informacoes(description):
    if isinstance(description, str):
        sistema_operacional = re.search(r'Operating System: ([^,]+)', description)
        ip_address = re.search(r'IP Address: ([^,]+)', description)
        modelo = re.search(r'Model: ([^,]+)', description)
        ultimo_usuario = re.search(r'Last User: ([^,]+)', description)

        return {
            'OperatingSystem': sistema_operacional.group(1) if sistema_operacional else None,
            'IPAddress': ip_address.group(1) if ip_address else None,
            'Model': modelo.group(1) if modelo else None,
            'LastUser': ultimo_usuario.group(1) if ultimo_usuario else None
        }
    else:
        return {
            'OperatingSystem': None,
            'IPAddress': None,
            'Model': None,
            'LastUser': None
        }

def extrair_faixa_ip(ip_address):
    return '.'.join(ip_address.split('.')[:3]) if isinstance(ip_address, str) else None

def mapear_unidade(ip_address):
    if not ip_address:
        return None
    faixa_ip = int(ip_address.split('.')[2])  # Pega a terceira parte do IP
    if 101 <= faixa_ip <= 111 or faixa_ip in [112, 124, 126]:
        return 'SEDE'
    elif 211 <= faixa_ip <= 218:
        return 'JCC'
    elif faixa_ip == 94:
        return 'SSJ'
    elif faixa_ip == 93:
        return 'POSTO PORTO REAL DO COLÉGIO'
    elif faixa_ip == 71:
        return 'POSTO DE NOVO LINO'
    elif faixa_ip == 69:
        return 'POSTO DELMIRO GOVEIA'
    elif faixa_ip == 88:
        return 'GALPÃO'
    elif faixa_ip == 80:
        return 'CORREIOS TABULEIRO'
    elif faixa_ip == 87:
        return 'CORREFAZ'
    elif faixa_ip == 64:
        return 'ARAPIRACA'
    return 'OUTRA'

def padronizar_modelo(modelo):
    modelos_unificados = {
        "HP ProBook 445 G8": ["HP ProBook 445 G8 Notebook PC", "HP ProBook 445 G8n", "HP ProBrook 445 G8", "HP ProBooK 445 G8n", "HP ProBook 445G8"]
    }
    for padrao, variantes in modelos_unificados.items():
        if modelo in variantes:
            return padrao
    return modelo

def main():
    st.set_page_config(layout="wide")  # Configura o layout como amplo
    st.title("Dashboard de Monitoramento de Computadores")

    # Carregar o arquivo CSV na barra lateral
    st.sidebar.header("Carregar Arquivo")
    uploaded_file = st.sidebar.file_uploader("Faça upload do arquivo CSV", type="csv")
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, delimiter=';', decimal=",", encoding="ISO-8859-1")

            if 'Description' in df.columns and 'Name' in df.columns:
                # Filtrar apenas computadores e notebooks
                df = df[df['Name'].str.contains('ESTA|NOTE', case=False, na=False)]
                
                informacoes_extraidas = df['Description'].apply(extrair_informacoes).apply(pd.Series)
                informacoes_extraidas['FaixaIP'] = informacoes_extraidas['IPAddress'].apply(extrair_faixa_ip)
                informacoes_extraidas['Unidade'] = informacoes_extraidas['IPAddress'].apply(mapear_unidade)
                informacoes_extraidas['Modelo'] = informacoes_extraidas['Model'].apply(padronizar_modelo)
                
                df_resultado = pd.concat([df[['Name']], informacoes_extraidas], axis=1)

                st.sidebar.subheader("Filtros")
                sistema_filtrado = st.sidebar.multiselect("Filtrar por SO", options=df_resultado['OperatingSystem'].dropna().unique())
                unidade_filtrada = st.sidebar.multiselect("Filtrar por Unidade", options=df_resultado['Unidade'].dropna().unique())

                if sistema_filtrado:
                    df_resultado = df_resultado[df_resultado['OperatingSystem'].isin(sistema_filtrado)]
                if unidade_filtrada:
                    df_resultado = df_resultado[df_resultado['Unidade'].isin(unidade_filtrada)]

                # Layout com os gráficos lado a lado
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Contagem por Faixa IP")
                    faixa_count = df_resultado['FaixaIP'].value_counts()
                    st.bar_chart(faixa_count)
                    st.write("Total por Faixa IP:", faixa_count.sum())

                    # Checkbox para exibir a lista completa
                    if st.checkbox("Mostrar lista completa de Faixa IP"):
                        st.write(faixa_count)

                with col2:
                    st.subheader("Contagem por SO")
                    sistema_count = df_resultado['OperatingSystem'].value_counts()
                    st.bar_chart(sistema_count)
                    st.write("Total por Sistema Operacional:", sistema_count.sum())

                    # Checkbox para exibir a lista completa
                    if st.checkbox("Mostrar lista completa de Sistemas Operacionais"):
                        st.write(sistema_count)

                st.write("")  # Espaço entre os gráficos

                # Nova linha para os próximos gráficos
                col3, col4 = st.columns(2)

                with col3:
                    st.subheader("Contagem por Modelo")
                    modelo_count = df_resultado['Modelo'].value_counts()
                    st.bar_chart(modelo_count)
                    st.write("Total por Modelo:", modelo_count.sum())

                    # Checkbox para exibir a lista completa
                    if st.checkbox("Mostrar lista completa de Modelos"):
                        st.write(modelo_count)

                with col4:
                    st.subheader("Contagem por Unidade")
                    unidade_count = df_resultado['Unidade'].value_counts()
                    st.bar_chart(unidade_count)
                    st.write("Total por Unidade:", unidade_count.sum())

                    # Checkbox para exibir a lista completa
                    if st.checkbox("Mostrar lista completa por Unidade"):
                        st.write(unidade_count)

                # Mostrar totais ao final
                st.subheader("Totais")
                totais = [
                    {"Categoria": "Total por Faixa IP", "Total": faixa_count.sum()},
                    {"Categoria": "Total por Sistema Operacional", "Total": sistema_count.sum()},
                    {"Categoria": "Total por Modelo", "Total": modelo_count.sum()},
                    {"Categoria": "Total por Unidade", "Total": unidade_count.sum()}
                ]
                st.write(pd.DataFrame(totais))

            else:
                st.error("O arquivo não contém as colunas 'Description' e 'Name'. Verifique o formato do arquivo.")
        
        except Exception as e:
            st.error(f"Erro ao ler o arquivo CSV: {e}")

if __name__ == "__main__":
    main()
