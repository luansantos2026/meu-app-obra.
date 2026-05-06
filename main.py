import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Gestor de Obra Pro", layout="wide")

st.title("🏗️ Gestor de Orçamentos e Obras")

# --- INICIALIZAÇÃO DE DADOS ---
if 'gastos' not in st.session_state:
    st.session_state.gastos = pd.DataFrame(columns=["Descrição", "Categoria", "Valor", "Data"])

if 'extras' not in st.session_state:
    st.session_state.extras = pd.DataFrame(columns=["Descrição", "Valor", "Data", "Status"])

if 'materiais' not in st.session_state:
    # Tabela de materiais com colunas de custo
    st.session_state.materiais = pd.DataFrame(columns=["Item", "Quantidade", "Unidade", "Preço Unit. (R$)", "Total (R$)", "Status"])

# Barra Lateral
st.sidebar.header("⚙️ Configurações")
orcamento_base = st.sidebar.number_input("Orçamento Base (R$)", min_value=0.0, value=50000.0)

# --- NAVEGAÇÃO POR ABAS ---
tab1, tab2, tab3 = st.tabs(["📊 Financeiro", "➕ Serviços Extras", "📋 Lista de Materiais"])

# ABA 1: FINANCEIRO
with tab1:
    st.header("Controle de Custos da Obra")
    total_gasto = st.session_state.gastos["Valor"].sum()
    st.metric("Total Gasto", f"R$ {total_gasto:,.2f}", delta=f"Saldo: R$ {orcamento_base - total_gasto:,.2f}")
    st.dataframe(st.session_state.gastos, use_container_width=True)

# ABA 2: EXTRAS
with tab2:
    st.header("Serviços Fora do Orçamento")
    with st.form("form_extra"):
        desc_ex = st.text_input("Descrição do Extra")
        val_ex = st.number_input("Valor Cobrado (R$)", min_value=0.0)
        if st.form_submit_button("Adicionar"):
            novo_ex = pd.DataFrame([{"Descrição": desc_ex, "Valor": val_ex, "Data": datetime.now().strftime("%d/%m/%Y"), "Status": "Pendente"}])
            st.session_state.extras = pd.concat([st.session_state.extras, novo_ex], ignore_index=True)
            st.rerun()
    st.table(st.session_state.extras)

# ABA 3: LISTA DE MATERIAIS (COM CÁLCULO DE PREÇO)
with tab3:
    st.header("Lista Detalhada de Materiais e Custos")
    
    with st.expander("➕ Adicionar Novo Material"):
        with st.form("form_material"):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
            item = col1.text_input("Material (Ex: Porcelanato)")
            qtd = col2.number_input("Qtd", min_value=0.0, step=1.0)
            unid = col3.selectbox("Unid.", ["m²", "Sacos", "Unid", "Kg", "Latas"])
            preco_un = col4.number_input("Preço Unitário (R$)", min_value=0.0)
            
            status_mat = st.selectbox("Status", ["Para Comprar", "Comprado", "Entregue"])
            
            if st.form_submit_button("Incluir na Lista"):
                if item:
                    # Cálculo automático do total do item
                    total_item = qtd * preco_un
                    novo_mat = pd.DataFrame([{
                        "Item": item, 
                        "Quantidade": qtd, 
                        "Unidade": unid, 
                        "Preço Unit. (R$)": preco_un,
                        "Total (R$)": total_item,
                        "Status": status_mat
                    }])
                    st.session_state.materiais = pd.concat([st.session_state.materiais, novo_mat], ignore_index=True)
                    st.success(f"Registrado: {item}")
                    st.rerun()

    if not st.session_state.materiais.empty:
        # Resumo da lista de materiais
        soma_materiais = st.session_state.materiais["Total (R$)"].sum()
        st.info(f"💰 **Soma Total dos Materiais Listados: R$ {soma_materiais:,.2f}**")
        
        st.subheader("Itens na Lista")
        st.dataframe(st.session_state.materiais, use_container_width=True)
        
        if st.button("Limpar Lista"):
            st.session_state.materiais = pd.DataFrame(columns=["Item", "Quantidade", "Unidade", "Preço Unit. (R$)", "Total (R$)", "Status"])
            st.rerun()
