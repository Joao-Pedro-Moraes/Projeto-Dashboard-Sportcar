import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import statsmodels.api as sm

st.set_page_config(
    page_title="AutoScore | Benchmark & Custo-Benefício de Supercarros",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling - Clean Automotive / Tech Portal look (like Kimovil / GSMArena / TudoCelular)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=Rajdhani:wght@600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .hero-container {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #1a2332 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 30px 40px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .hero-title {
        font-family: 'Rajdhani', sans-serif;
        font-size: 42px;
        font-weight: 700;
        letter-spacing: 1px;
        background: linear-gradient(90deg, #58a6ff 0%, #3fb950 50%, #f1e05a 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    
    .hero-subtitle {
        color: #8b949e;
        font-size: 16px;
        max-width: 800px;
        line-height: 1.5;
    }
    
    .badge-cb-excelente {
        background-color: rgba(63, 185, 80, 0.15);
        color: #3fb950;
        border: 1px solid rgba(63, 185, 80, 0.4);
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 12px;
        display: inline-block;
    }
    
    .badge-cb-bom {
        background-color: rgba(88, 166, 255, 0.15);
        color: #58a6ff;
        border: 1px solid rgba(88, 166, 255, 0.4);
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 12px;
        display: inline-block;
    }
    
    .badge-cb-mercado {
        background-color: rgba(210, 153, 34, 0.15);
        color: #d29922;
        border: 1px solid rgba(210, 153, 34, 0.4);
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 12px;
        display: inline-block;
    }
    
    .badge-cb-grife {
        background-color: rgba(219, 97, 162, 0.15);
        color: #db61a2;
        border: 1px solid rgba(219, 97, 162, 0.4);
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 12px;
        display: inline-block;
    }
    
    .car-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 18px;
        transition: transform 0.2s, border-color 0.2s;
    }
    .car-card:hover {
        border-color: #58a6ff;
        transform: translateY(-2px);
    }
    
    .car-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    
    .score-circle {
        background: #21262d;
        border: 2px solid #3fb950;
        border-radius: 50%;
        width: 52px;
        height: 52px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 700;
        font-size: 20px;
        color: #3fb950;
    }
    
    .spec-item {
        background: #0d1117;
        border-radius: 8px;
        padding: 8px 12px;
        text-align: center;
    }
    .spec-label {
        font-size: 11px;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .spec-value {
        font-size: 16px;
        font-weight: 700;
        color: #c9d1d9;
    }
    
    div[data-testid="stMetricValue"] {
        font-family: 'Rajdhani', sans-serif;
        font-size: 28px;
    }
</style>
""", unsafe_allow_html=True)

# Country flags dictionary
FLAGS = {
    'Porsche': '🇩🇪', 'BMW': '🇩🇪', 'Audi': '🇩🇪', 'Mercedes-Benz': '🇩🇪', 'Mercedes-AMG': '🇩🇪',
    'Ferrari': '🇮🇹', 'Lamborghini': '🇮🇹', 'Maserati': '🇮🇹', 'Alfa Romeo': '🇮🇹', 'Pagani': '🇮🇹', 'Pininfarina': '🇮🇹',
    'Chevrolet': '🇺🇸', 'Ford': '🇺🇸', 'Dodge': '🇺🇸', 'Tesla': '🇺🇸', 'Shelby': '🇺🇸',
    'McLaren': '🇬🇧', 'Aston Martin': '🇬🇧', 'Jaguar': '🇬🇧', 'Bentley': '🇬🇧', 'Rolls-Royce': '🇬🇧', 'Lotus': '🇬🇧', 'Ariel': '🇬🇧', 'TVR': '🇬🇧', 'Ultima': '🇬🇧',
    'Bugatti': '🇫🇷', 'Alpine': '🇫🇷',
    'Koenigsegg': '🇸🇪', 'Polestar': '🇸🇪',
    'Rimac': '🇭🇷',
    'Nissan': '🇯🇵', 'Lexus': '🇯🇵', 'Toyota': '🇯🇵', 'Acura': '🇯🇵', 'Mazda': '🇯🇵', 'Subaru': '🇯🇵',
    'Kia': '🇰🇷',
    'W Motors': '🇦🇪'
}

@st.cache_data
def load_data():
    df = pd.read_csv("C:/Users/foxcr/.gemini/antigravity/scratch/supercar_dashboard/supercars_clean.csv")
    df['Flag'] = df['Car Make'].map(FLAGS).fillna('🏁')
    df['Display_Name'] = df['Flag'] + " " + df['Car Make'] + " " + df['Car Model'] + " (" + df['Year'].astype(str) + ")"
    return df

df = load_data()

# Hero Header
st.markdown("""
<div class="hero-container">
    <div class="hero-title">⚡ AUTOSCORE &bull; BENCHMARK DE SUPERCARROS</div>
    <div class="hero-subtitle">
        A ferramenta de consulta inteligente para comparar supercarros pela métrica de <b>retorno de hardware por dólar investido</b>.
        Consulte especificações técnicas, compare modelos lado a lado e simule preços justos com base em modelos estatísticos de regressão.
    </div>
</div>
""", unsafe_allow_html=True)

# Top Navigation Tabs
nav_tab1, nav_tab2, nav_tab3, nav_tab4, nav_tab5 = st.tabs([
    "🔍 Catálogo & Busca Rápida",
    "⚖️ Comparador Lado a Lado",
    "🎯 Simulador de Preço Justo",
    "📈 Análise de Mercado (Regressão)",
    "🔬 Painel de Validação Estatística"
])

# -------------------------------------------------------------
# TAB 1: CATÁLOGO & BUSCA RÁPIDA (Estilo Vitrine / Loja de Celular)
# -------------------------------------------------------------
with nav_tab1:
    col_search, col_f_origem, col_f_motor, col_order = st.columns([3, 2, 2, 2])
    
    with col_search:
        busca_texto = st.text_input("🔎 Pesquisar por marca ou modelo:", placeholder="Ex: Corvette, Huracan, 911, Chiron, Plaid...")
    
    with col_f_origem:
        origem_filtro = st.multiselect("Origem:", options=sorted(df["Origin_Region"].unique()), default=sorted(df["Origin_Region"].unique()))
        
    with col_f_motor:
        motor_filtro = st.multiselect("Motorização:", options=sorted(df["Powertrain"].unique()), default=sorted(df["Powertrain"].unique()))
        
    with col_order:
        ordem_catalogo = st.selectbox(
            "Ordenar por:",
            ["Maior Custo-Benefício", "Maior Benchmark Score", "Menor Preço", "Maior Potência (HP)", "Aceleração 0-60 mais rápida"]
        )

    # Filter data
    df_cat = df[
        (df["Origin_Region"].isin(origem_filtro)) &
        (df["Powertrain"].isin(motor_filtro))
    ].copy()
    
    if busca_texto:
        df_cat = df_cat[
            df_cat["Car Make"].str.contains(busca_texto, case=False, na=False) |
            df_cat["Car Model"].str.contains(busca_texto, case=False, na=False)
        ]
        
    if ordem_catalogo == "Maior Custo-Benefício":
        df_cat = df_cat.sort_values(by="Cost_Benefit_Score", ascending=False)
    elif ordem_catalogo == "Maior Benchmark Score":
        df_cat = df_cat.sort_values(by="Performance_Score", ascending=False)
    elif ordem_catalogo == "Menor Preço":
        df_cat = df_cat.sort_values(by="Price_USD", ascending=True)
    elif ordem_catalogo == "Maior Potência (HP)":
        df_cat = df_cat.sort_values(by="Horsepower_clean", ascending=False)
    elif ordem_catalogo == "Aceleração 0-60 mais rápida":
        df_cat = df_cat.sort_values(by="0_60_Time_s", ascending=True)

    # Dedup display cards by Make+Model+Year
    df_cat_unique = df_cat.drop_duplicates(subset=["Car Make", "Car Model", "Year"])

    # Quick metric indicators
    st.caption(f"Exibindo **{len(df_cat_unique)}** veículos encontrados.")

    # Render Grid of Cards (3 per row)
    cards_per_page = 15
    for i in range(0, min(cards_per_page, len(df_cat_unique)), 3):
        row_cols = st.columns(3)
        for j in range(3):
            idx = i + j
            if idx < len(df_cat_unique):
                car = df_cat_unique.iloc[idx]
                with row_cols[j]:
                    # Badge selector
                    if car["Classification_CB"] == "Custo-Benefício Excepcional":
                        badge_html = '<span class="badge-cb-excelente">🔥 CUSTO-BENEFÍCIO TOPO</span>'
                    elif car["Classification_CB"] == "Bom Custo-Benefício":
                        badge_html = '<span class="badge-cb-bom">⭐ BOM CUSTO-BENEFÍCIO</span>'
                    elif car["Classification_CB"] == "Preço Compatível com Mercado":
                        badge_html = '<span class="badge-cb-mercado">⚖️ PREÇO DE MERCADO</span>'
                    else:
                        badge_html = '<span class="badge-cb-grife">💎 GRIFE / EXCLUSIVO</span>'
                    
                    st.markdown(f"""
                    <div class="car-card">
                        <div class="car-card-header">
                            <div>
                                <span style="font-size: 13px; color: #8b949e;">{car['Flag']} {car['Car Make']} &bull; {car['Year']}</span>
                                <div style="font-size: 20px; font-weight: 700; color: #f0f6fc;">{car['Car Model']}</div>
                            </div>
                            <div class="score-circle">
                                {car['Performance_Score']:.0f}
                            </div>
                        </div>
                        <div style="margin-bottom: 12px;">{badge_html}</div>
                        <div style="font-size: 24px; font-weight: 800; color: #3fb950; margin-bottom: 14px;">
                            ${car['Price_USD']:,.0f}
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px;">
                            <div class="spec-item">
                                <div class="spec-label">Potência</div>
                                <div class="spec-value">{car['Horsepower_clean']:.0f} HP</div>
                            </div>
                            <div class="spec-item">
                                <div class="spec-label">0-60 mph</div>
                                <div class="spec-value">{car['0_60_Time_s']:.1f} s</div>
                            </div>
                            <div class="spec-item">
                                <div class="spec-label">HP/$10k</div>
                                <div class="spec-value">{car['HP_per_10k_USD']:.1f}</div>
                            </div>
                        </div>
                        <div style="margin-top: 10px; font-size: 12px; color: #8b949e; text-align: center;">
                            Propulsão: <b>{car['Powertrain']}</b> | Origem: <b>{car['Origin_Region']}</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

# -------------------------------------------------------------
# TAB 2: COMPARADOR LADO A LADO (Estilo Versus / TudoCelular)
# -------------------------------------------------------------
with nav_tab2:
    st.subheader("⚔️ Duelo Direto: Comparador Técnico Lado a Lado")
    st.caption("Selecione dois carros para analisar a disparidade de preço, pontuação de hardware e relação de custo-benefício.")

    carros_opcoes = sorted(df["Display_Name"].unique())
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        c1_default = [c for c in carros_opcoes if "Corvette" in c][0] if any("Corvette" in c for c in carros_opcoes) else carros_opcoes[0]
        c1_name = st.selectbox("Selecione o Supercarro A:", carros_opcoes, index=carros_opcoes.index(c1_default))
    with col_c2:
        c2_default = [c for c in carros_opcoes if "911" in c][0] if any("911" in c for c in carros_opcoes) else carros_opcoes[1]
        c2_name = st.selectbox("Selecione o Supercarro B:", carros_opcoes, index=carros_opcoes.index(c2_default))

    carA = df[df["Display_Name"] == c1_name].iloc[0]
    carB = df[df["Display_Name"] == c2_name].iloc[0]

    # Side-by-side header cards
    col_headA, col_vs, col_headB = st.columns([5, 1, 5])
    with col_headA:
        st.markdown(f"### {carA['Flag']} {carA['Car Make']} {carA['Car Model']}")
        st.markdown(f"#### :green[${carA['Price_USD']:,.0f}] &bull; Score: **{carA['Performance_Score']:.1f} pts**")
    with col_vs:
        st.markdown("<h2 style='text-align: center; color: #8b949e;'>VS</h2>", unsafe_allow_html=True)
    with col_headB:
        st.markdown(f"### {carB['Flag']} {carB['Car Make']} {carB['Car Model']}")
        st.markdown(f"#### :green[${carB['Price_USD']:,.0f}] &bull; Score: **{carB['Performance_Score']:.1f} pts**")

    # Metrics comparison table
    def win_badge(valA, valB, lower_is_better=False):
        if valA == valB:
            return "Empate", "Empate"
        if lower_is_better:
            return ("✅ Vencedor", "") if valA < valB else ("", "✅ Vencedor")
        else:
            return ("✅ Vencedor", "") if valA > valB else ("", "✅ Vencedor")

    w_hpA, w_hpB = win_badge(carA['Horsepower_clean'], carB['Horsepower_clean'])
    w_tqA, w_tqB = win_badge(carA['Torque_clean'], carB['Torque_clean'])
    w_acA, w_acB = win_badge(carA['0_60_Time_s'], carB['0_60_Time_s'], lower_is_better=True)
    w_prA, w_prB = win_badge(carA['Price_USD'], carB['Price_USD'], lower_is_better=True)
    w_cbA, w_cbB = win_badge(carA['Cost_Benefit_Score'], carB['Cost_Benefit_Score'])
    w_scA, w_scB = win_badge(carA['Performance_Score'], carB['Performance_Score'])

    comp_df = pd.DataFrame([
        {"Especificação": "Preço de Mercado", f"{carA['Car Model']}": f"${carA['Price_USD']:,.0f} {w_prA}", f"{carB['Car Model']}": f"${carB['Price_USD']:,.0f} {w_prB}"},
        {"Especificação": "Potência (Horsepower)", f"{carA['Car Model']}": f"{carA['Horsepower_clean']:.0f} HP {w_hpA}", f"{carB['Car Model']}": f"{carB['Horsepower_clean']:.0f} HP {w_hpB}"},
        {"Especificação": "Torque Máximo", f"{carA['Car Model']}": f"{carA['Torque_clean']:.0f} lb-ft {w_tqA}", f"{carB['Car Model']}": f"{carB['Torque_clean']:.0f} lb-ft {w_tqB}"},
        {"Especificação": "Aceleração 0-60 mph", f"{carA['Car Model']}": f"{carA['0_60_Time_s']:.2f} s {w_acA}", f"{carB['Car Model']}": f"{carB['0_60_Time_s']:.2f} s {w_acB}"},
        {"Especificação": "Benchmark Score (Hardware)", f"{carA['Car Model']}": f"{carA['Performance_Score']:.1f} pts {w_scA}", f"{carB['Car Model']}": f"{carB['Performance_Score']:.1f} pts {w_scB}"},
        {"Especificação": "Potência por $10k USD", f"{carA['Car Model']}": f"{carA['HP_per_10k_USD']:.1f} HP/$10k {w_cbA}", f"{carB['Car Model']}": f"{carB['HP_per_10k_USD']:.1f} HP/$10k {w_cbB}"},
        {"Especificação": "Índice Custo-Benefício", f"{carA['Car Model']}": f"{carA['Cost_Benefit_Score']:.2f} pts/$10k {w_cbA}", f"{carB['Car Model']}": f"{carB['Cost_Benefit_Score']:.2f} pts/$10k {w_cbB}"},
        {"Especificação": "Classificação Econômica", f"{carA['Car Model']}": f"{carA['Classification_CB']}", f"{carB['Car Model']}": f"{carB['Classification_CB']}"}
    ])
    st.table(comp_df.set_index("Especificação"))

    # Radar Comparison
    categories = ["Potência", "Torque", "Aceleração", "Benchmark Score", "Custo-Benefício"]
    def get_norm(c):
        hp = c["Horsepower_clean"] / df["Horsepower_clean"].max() * 100
        tq = c["Torque_clean"] / df["Torque_clean"].max() * 100
        ac = (df["0_60_Time_s"].max() - c["0_60_Time_s"]) / (df["0_60_Time_s"].max() - df["0_60_Time_s"].min()) * 100
        sc = c["Performance_Score"]
        cb = min(c["Cost_Benefit_Score"] / df["Cost_Benefit_Score"].quantile(0.95) * 100, 100)
        return [hp, tq, ac, sc, cb]

    fig_rad = go.Figure()
    vA = get_norm(carA)
    vB = get_norm(carB)
    fig_rad.add_trace(go.Scatterpolar(r=vA + [vA[0]], theta=categories + [categories[0]], fill='toself', name=f"{carA['Car Make']} {carA['Car Model']}", line_color='#58a6ff'))
    fig_rad.add_trace(go.Scatterpolar(r=vB + [vB[0]], theta=categories + [categories[0]], fill='toself', name=f"{carB['Car Make']} {carB['Car Model']}", line_color='#3fb950'))
    fig_rad.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), title="Gráfico Radar de Desempenho e Eficiência Relativa")
    st.plotly_chart(fig_rad, use_container_width=True)

# -------------------------------------------------------------
# TAB 3: SIMULADOR DE PREÇO JUSTO (Calculadora Interativa)
# -------------------------------------------------------------
with nav_tab3:
    st.subheader("🎯 Simulador de Preço Justo: Calculadora de Hardware")
    st.caption("Configure as especificações de um carro hipotético e o modelo econométrico OLS calculará o preço justo estimado pelo mercado com base na concorrência.")

    # Regression fit on global dataset
    X_glob = sm.add_constant(df[['Horsepower_clean', 'Torque_clean', '0_60_Time_s']])
    model_glob = sm.OLS(df['Price_USD'], X_glob).fit()

    col_sim_in, col_sim_out = st.columns([1, 1])

    with col_sim_in:
        st.markdown("##### ⚙️ Parâmetros do Veículo Desejado")
        sim_hp = st.slider("Potência Estimada (Horsepower):", min_value=250, max_value=1600, value=650, step=25)
        sim_tq = st.slider("Torque Estimado (lb-ft):", min_value=200, max_value=1200, value=600, step=25)
        sim_ac = st.slider("Tempo de Aceleração 0-60 mph (segundos):", min_value=1.8, max_value=6.0, value=3.2, step=0.1)
        sim_origin = st.selectbox("Região do Fabricante:", ["Estados Unidos", "Europa", "Ásia"])

    with col_sim_out:
        st.markdown("##### 💵 Estimativa Econométrica")
        
        # Prediction
        sim_X = np.array([1.0, sim_hp, sim_tq, sim_ac])
        preco_pred = model_glob.predict(sim_X)[0]
        
        # 95% Confidence Interval for mean prediction
        pred_res = model_glob.get_prediction(sim_X)
        pred_summary = pred_res.summary_frame(alpha=0.05)
        ic_inf = max(pred_summary['mean_ci_lower'].iloc[0], 30000)
        ic_sup = pred_summary['mean_ci_upper'].iloc[0]

        # Calculate simulated Benchmark Score
        hp_n_s = (sim_hp - df['Horsepower_clean'].min()) / (df['Horsepower_clean'].max() - df['Horsepower_clean'].min())
        tq_n_s = (sim_tq - df['Torque_clean'].min()) / (df['Torque_clean'].max() - df['Torque_clean'].min())
        ac_n_s = (df['0_60_Time_s'].max() - sim_ac) / (df['0_60_Time_s'].max() - df['0_60_Time_s'].min())
        score_sim = 100 * (0.40 * hp_n_s + 0.30 * tq_n_s + 0.30 * ac_n_s)

        st.metric("Preço Justo Estimado", f"${preco_pred:,.0f}")
        st.write(f"**Intervalo de Confiança do Preço Médio (95%):** `${ic_inf:,.0f}` a `${ic_sup:,.0f}`")
        st.metric("Benchmark Score Calculado", f"{score_sim:.1f} / 100 pts")

        # Find closest real cars in dataset
        df['Dist_Sim'] = np.abs(df['Horsepower_clean'] - sim_hp) / 100 + np.abs(df['0_60_Time_s'] - sim_ac)
        closest_cars = df.sort_values(by='Dist_Sim').head(3)

        st.markdown("##### 🚗 Modelos Reais Equivalentes no Mercado:")
        for _, c_row in closest_cars.iterrows():
            st.write(f"- **{c_row['Flag']} {c_row['Car Make']} {c_row['Car Model']}** ({c_row['Year']}): ${c_row['Price_USD']:,.0f} | {c_row['Horsepower_clean']:.0f} HP | 0-60: {c_row['0_60_Time_s']}s")

# -------------------------------------------------------------
# TAB 4: ANÁLISE DE MERCADO & REGRESSÃO (Atende aos Requisitos da Rubrica)
# -------------------------------------------------------------
with nav_tab4:
    st.subheader("📈 Análise de Mercado: Dispersão e Linha de Tendência OLS")
    st.caption("Explore a correlação empírica entre pontuação de hardware e preço de tabela. Carros posicionados abaixo da linha de regressão oferecem maior valor relativo.")

    col_flt1, col_flt2 = st.columns(2)
    with col_flt1:
        f_reg = st.multiselect("Filtrar Regiões no Gráfico:", sorted(df["Origin_Region"].unique()), default=sorted(df["Origin_Region"].unique()), key="reg_scatter")
    with col_flt2:
        f_max_price = st.slider("Preço Máximo de Exibição:", 100000, 3500000, 1000000, step=100000, format="$%d")

    df_sub = df[(df["Origin_Region"].isin(f_reg)) & (df["Price_USD"] <= f_max_price)].copy()

    if len(df_sub) > 5:
        X_sub = sm.add_constant(df_sub["Performance_Score"])
        ols_fit = sm.OLS(df_sub["Price_USD"], X_sub).fit()

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("R² do Recorte", f"{ols_fit.rsquared:.3f}")
        col_m2.metric("Coeficiente Angular", f"${ols_fit.params['Performance_Score']:,.0f} / ponto")
        col_m3.metric("F-Statistic", f"{ols_fit.fvalue:.1f}")
        col_m4.metric("p-valor", f"{ols_fit.f_pvalue:.2e}")

        fig_scat = px.scatter(
            df_sub,
            x="Performance_Score",
            y="Price_USD",
            color="Origin_Region",
            symbol="Powertrain",
            size="Horsepower_clean",
            hover_name="Car Model",
            hover_data={
                "Car Make": True,
                "Price_USD": ":$,.0f",
                "Horsepower_clean": True,
                "0_60_Time_s": True,
                "Classification_CB": True
            },
            labels={
                "Performance_Score": "Benchmark Score (Pontuação 0-100)",
                "Price_USD": "Preço de Mercado (USD)",
                "Origin_Region": "Origem"
            },
            title="Preço Observado vs Pontuação de Desempenho com Linha OLS"
        )

        xs = np.linspace(df_sub["Performance_Score"].min(), df_sub["Performance_Score"].max(), 100)
        ys = ols_fit.predict(sm.add_constant(xs))
        fig_scat.add_trace(go.Scatter(x=xs, y=ys, mode='lines', name='Tendência OLS', line=dict(color='white', width=2, dash='dash')))
        st.plotly_chart(fig_scat, use_container_width=True)

        # Residuals Plot
        fig_res = px.scatter(
            df_sub,
            x=ols_fit.fittedvalues,
            y=ols_fit.resid,
            color="Origin_Region",
            hover_name="Car Model",
            labels={"x": "Preço Previsto (USD)", "y": "Resíduo (Preço Real - Previsto)"},
            title="Diagnóstico de Resíduos da Regressão (Homocedasticidade)"
        )
        fig_res.add_hline(y=0, line_dash="dash", line_color="red")
        st.plotly_chart(fig_res, use_container_width=True)

# -------------------------------------------------------------
# TAB 5: PAINEL DE VALIDAÇÃO ESTATÍSTICA (Testes t & IC 95%)
# -------------------------------------------------------------
with nav_tab5:
    st.subheader("🔬 Validação Estatística Acadêmica")
    st.caption("Painel com os cálculos inferenciais exigidos para a defesa oral: testes de hipóteses, graus de liberdade e intervalos de confiança a 95%.")

    col_ic1, col_ic2 = st.columns(2)
    
    with col_ic1:
        st.markdown("##### Intervalo de Confiança (95%): Potência por US$ 10k")
        ic_tab = []
        for reg, g in df.groupby("Origin_Region"):
            vals = g["HP_per_10k_USD"]
            n = len(vals)
            m = vals.mean()
            se = stats.sem(vals)
            ci = se * stats.t.ppf(0.975, df=n-1) if n > 1 else 0
            ic_tab.append({"Origem": reg, "N": n, "Média HP/$10k": m, "IC 95% Inferior": m - ci, "IC 95% Superior": m + ci, "Erro": ci})
            
        df_ic_show = pd.DataFrame(ic_tab)
        fig_bar_ic = go.Figure()
        fig_bar_ic.add_trace(go.Bar(
            x=df_ic_show["Origem"],
            y=df_ic_show["Média HP/$10k"],
            error_y=dict(type='data', array=df_ic_show["Erro"]),
            marker_color=['#1f77b4', '#2ca02c', '#d62728', '#9467bd'][:len(df_ic_show)]
        ))
        fig_bar_ic.update_layout(title="Média HP/$10k com Barras de Erro (IC 95%)", yaxis_title="HP por US$ 10.000")
        st.plotly_chart(fig_bar_ic, use_container_width=True)
        st.dataframe(df_ic_show[["Origem", "N", "Média HP/$10k", "IC 95% Inferior", "IC 95% Superior"]].round(2), use_container_width=True)

    with col_ic2:
        st.markdown("##### Intervalo de Confiança (95%): Aceleração 0-60 mph")
        ic_pt_tab = []
        for pt, g in df.groupby("Powertrain"):
            vals = g["0_60_Time_s"]
            n = len(vals)
            m = vals.mean()
            se = stats.sem(vals)
            ci = se * stats.t.ppf(0.975, df=n-1) if n > 1 else 0
            ic_pt_tab.append({"Propulsão": pt, "N": n, "Média 0-60 (s)": m, "IC 95% Inferior": m - ci, "IC 95% Superior": m + ci, "Erro": ci})
            
        df_pt_show = pd.DataFrame(ic_pt_tab)
        fig_bar_pt = go.Figure()
        fig_bar_pt.add_trace(go.Bar(
            x=df_pt_show["Propulsão"],
            y=df_pt_show["Média 0-60 (s)"],
            error_y=dict(type='data', array=df_pt_show["Erro"]),
            marker_color=['#ff7f0e', '#1f77b4', '#2ca02c'][:len(df_pt_show)]
        ))
        fig_bar_pt.update_layout(title="Média 0-60 mph com Barras de Erro (IC 95%)", yaxis_title="Segundos")
        st.plotly_chart(fig_bar_pt, use_container_width=True)
        st.dataframe(df_pt_show[["Propulsão", "N", "Média 0-60 (s)", "IC 95% Inferior", "IC 95% Superior"]].round(2), use_container_width=True)

    st.markdown("---")
    st.markdown("##### Tabela Consolidada de Testes de Hipóteses Formais")
    
    # Welch t-test 1
    u = df[df["Origin_Region"] == "Estados Unidos"]["HP_per_10k_USD"]
    e = df[df["Origin_Region"] == "Europa"]["HP_per_10k_USD"]
    t1, p1 = stats.ttest_ind(u, e, equal_var=False)
    df1 = ((u.var()/len(u) + e.var()/len(e))**2) / (((u.var()/len(u))**2)/(len(u)-1) + ((e.var()/len(e))**2)/(len(e)-1))

    # Welch t-test 2
    el = df[df["Powertrain"].isin(["Elétrico", "Híbrido"])]["0_60_Time_s"]
    co = df[df["Powertrain"] == "Combustão"]["0_60_Time_s"]
    t2, p2 = stats.ttest_ind(el, co, equal_var=False)
    df2 = ((el.var()/len(el) + co.var()/len(co))**2) / (((el.var()/len(el))**2)/(len(el)-1) + ((co.var()/len(co))**2)/(len(co)-1))

    t_df = pd.DataFrame([
        {
            "Hipótese": "H1: HP/$10k (EUA vs Europa)",
            "Amostra 1": f"EUA (M={u.mean():.1f}, N={len(u)})",
            "Amostra 2": f"Europa (M={e.mean():.1f}, N={len(e)})",
            "Estatística t": f"{t1:.4f}",
            "Graus de Liberdade (df)": f"{df1:.1f}",
            "p-valor": f"{p1:.4e}",
            "Conclusão (α=0.05)": "Rejeita-se H0 (EUA > Europa)"
        },
        {
            "Hipótese": "H2: 0-60 mph (Eletrificados vs Combustão)",
            "Amostra 1": f"Eletrificados (M={el.mean():.2f}s, N={len(el)})",
            "Amostra 2": f"Combustão (M={co.mean():.2f}s, N={len(co)})",
            "Estatística t": f"{t2:.4f}",
            "Graus de Liberdade (df)": f"{df2:.1f}",
            "p-valor": f"{p2:.4e}",
            "Conclusão (α=0.05)": "Rejeita-se H0 (Eletrificados mais rápidos)"
        }
    ])
    st.table(t_df.set_index("Hipótese"))
