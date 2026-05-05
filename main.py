import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io

# --- CONFIGURAÇÃO E ESTILO ---
st.set_page_config(page_title="Gestor de Obra Pro", layout="wide")
st.markdown("""<style> .main { background-color: #f5f7f9; } </style>""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE DADOS ---
if 'gastos' not in st.session_state:
    st.session_state.gastos = []
if 'extras' not in st.session_state:
    st.session_state.extras = []

# --- FUNÇÃO PARA GERAR PDF ---
def gerar_relatorio_pdf(orcamento, gastos, extras):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Relatório Financeiro de Obra", ln=True, align='C')
    
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Data do Relatório: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.cell(200, 10, f"Orçamento Base: R$ {orcamento:,.2f}", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "Detalhamento de Gastos", ln=True)
    pdf.set_font("Arial", '', 10)
    for g in gastos:
        pdf.cell(200, 8, f"- {g['Descrição']} ({g['Categoria']}): R$ {g['Valor']:,.2f}", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    total_g = sum(item['Valor'] for item in gastos)
    pdf.cell(200, 10, f"Total Gasto: R$ {total_g:,.2f}", ln=True)
    
    output = io.BytesIO()
    pdf_output = pdf.output(dest='S').encode('latin-1')
    output.write(pdf_output)
    return output.getvalue()

# --- INTERFACE ---
st.title("🏗️ Gestor de Obra Pro")
st.sidebar.header("Configurações do Projeto")
orcamento_base = st.sidebar.number_input("Orçamento Base (R$)", value=50000.0)

tab1, tab2, tab3 = st.tabs(["📊 Financeiro Principal", "➕ Aditivos/Extras", "📄 Relatórios & PDF"])

with tab1:
    st.header("Controle de Custos")
    with st.form("form_gastos"):
        col1, col2 = st.columns(2)
        desc = col1.text_input("Descrição do Item")
        cat = col2.selectbox("Categoria", ["Materiais", "Mão de Obra", "Outros"])
        val = st.number_input("Valor (R$)", min_value=0.0)
        recibo = st.file_uploader("Anexar Foto do Recibo", type=["jpg", "png", "pdf"])
        if st.form_submit_button("Registrar Gasto"):
            st.session_state.gastos.append({"Descrição": desc, "Categoria": cat, "Valor": val, "Data": datetime.now()})
            st.success("Gasto e Recibo registrados!")

    df_gastos = pd.DataFrame(st.session_state.gastos)
    if not df_gastos.empty:
        st.dataframe(df_gastos, use_container_width=True)

with tab2:
    st.header("Serviços Extras (Fora do Orçamento)")
    with st.form("form_extras"):
        desc_e = st.text_input("Descrição do Serviço Extra")
        val_e = st.number_input("Valor Adicional (R$)", min_value=0.0)
        status = st.selectbox("Status", ["Aguardando Aprovação", "Aprovado", "Pago"])
        if st.form_submit_button("Adicionar Extra"):
            st.session_state.extras.append({"Descrição": desc_e, "Valor": val_e, "Status": status})
    
    df_extras = pd.DataFrame(st.session_state.extras)
    if not df_extras.empty:
        st.table(df_extras)

with tab3:
    st.header("Exportação de Relatórios")
    if st.button("Gerar Relatório em PDF"):
        pdf_data = gerar_relatorio_pdf(orcamento_base, st.session_state.gastos, st.session_state.extras)
        st.download_button(label="📥 Baixar PDF para o Cliente", data=pdf_data, file_name="relatorio_obra.pdf", mime="application/pdf")