import streamlit as st
import sqlite3

def connect():
    return sqlite3.connect("clientes_completo.db")

def interpretacao(query):
    query = query.lower()    
    if "estados" in query and "clientes" in query:
        return {"tipo_consulta": "tabela_estados"}
    elif "whatsapp" in query and "2024" in query:
        return {"tipo_consulta": "campanha_whatsapp"}
    elif "categorias" in query and "produto" in query:
        return {"tipo_consulta": "categorias"}
    elif "reclamações" in query and "canal" in query:
        return {"tipo_consulta": "reclamacoes"}
    else:
        return {"tipo_consulta": "desconhecido"}

def consulta(instrucao, conn):
    cursor = conn.cursor()
    tipo_consulta = instrucao["tipo_consulta"]
    if tipo_consulta == "tabela_estados":
        cursor.execute("""
            SELECT estado, COUNT(*) as clientes
            FROM clientes c
            JOIN compras cp ON c.id = cp.cliente_id
            WHERE strftime('%m', cp.data_compra) = '05'
            GROUP BY estado
            ORDER BY clientes DESC
            LIMIT 5
        """)
        return cursor.fetchall()
    elif tipo_consulta == "campanha_whatsapp":
        cursor.execute("""
            SELECT COUNT(DISTINCT cliente_id)
            FROM campanhas_marketing
            WHERE canal = 'WhatsApp'
              AND interagiu = 1
              AND strftime('%Y', data_envio) = '2024'
        """)
        return cursor.fetchone()
    elif tipo_consulta == "categorias":
        cursor.execute("""
            SELECT categoria,
                   ROUND(AVG(total), 2) as media_por_cliente
            FROM (
                SELECT cliente_id, categoria, COUNT(*) as total
                FROM compras
                GROUP BY cliente_id, categoria
            )
            GROUP BY categoria
            ORDER BY media_por_cliente DESC
        """)
        return cursor.fetchall()
    elif tipo_consulta == "reclamacoes":
        cursor.execute("""
            SELECT canal, COUNT(*) as nao_resolvidas
            FROM suporte
            WHERE resolvido = 0
            GROUP BY canal
        """)
        return cursor.fetchall()
    else:
        return None

def resposta(instrucao, resultado):
    tipo_consulta = instrucao["tipo_consulta"]
    if tipo_consulta == "tabela_estados":
        st.write("Estados com maior número de clientes:")
        st.table(resultado)
    elif tipo_consulta == "campanha_whatsapp":
        st.metric("Clientes que interagiram via WhatsApp:", resultado[0])
    elif tipo_consulta == "categorias":
        st.write("Média de compras por cliente:")
        st.table(resultado)
    elif tipo_consulta == "reclamacoes":
        st.write("Reclamações não resolvidas por canal:")
        canais = [r[0] for r in resultado]
        valores = [r[1] for r in resultado]
        dados = dict(zip(canais, valores))
        st.bar_chart(list(dados.values()), height=400)
    else:
        st.warning("Não entendi sua solicitação :( Tente novamente!")

st.title("Desafio técnico em automação com IA 🦾")

pergunta = st.text_area("Faça sua consulta ao banco de dados :)",
                        height=100)

if st.button("Executar"):
    conn = connect()
    instrucao = interpretacao(pergunta)      
    resultado = consulta(instrucao, conn) 
    resposta(instrucao, resultado)        
    conn.close()
