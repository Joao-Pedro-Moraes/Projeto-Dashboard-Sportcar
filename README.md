# 🏎️ Projeto-Dashboard-Sportcar

**Supercar Benchmark & Custo-Benefício** — Análise exploratória, testes de hipóteses e regressão linear aplicados ao mercado de supercarros e hipercarros.

---

## 👥 Integrantes

- João Pedro Martins
- Gustavo Alencar
- Manoel D. Christo

---

## 📌 Sobre o projeto

Este projeto estuda a **precificação e a eficiência de desempenho** no segmento de supercarros e hipercarros. Inspirado nos benchmarks de smartphones (como AnTuTu e Geekbench), a ideia é transformar as especificações mecânicas brutas dos veículos — potência, torque e aceleração 0-60 mph — em um **índice padronizado de desempenho** e compará-lo com os preços praticados no mercado.

Os resultados da análise são apresentados em um **dashboard** (`app.py`), que torna a comparação entre desempenho e preço mais visual e interativa.

Com inferência estatística e modelagem econométrica, buscamos:

- identificar **anomalias de precificação**;
- verificar se a **origem geográfica** do fabricante influencia o custo por cavalo-vapor;
- estimar o **valor justo** de cada veículo com base em seus atributos tangíveis.

---

## 🔧 O que foi feito

1. **Tratamento dos dados** (`raw_supercars.csv`): remoção de duplicatas, limpeza de preços, tempos de aceleração, potência e torque (valores como `< 1.9` ou `1000+`) e padronização das especificações de motor.
2. **Engenharia de variáveis**:
   - `Origin_Region`: região do fabricante (Estados Unidos, Europa, Ásia, Oriente Médio);
   - `Powertrain`: tipo de motorização (Combustão, Híbrido, Elétrico);
   - `Performance_Score`: índice de 0 a 100 (40% potência, 30% torque, 30% aceleração invertida);
   - `HP_per_10k_USD`: cavalos-vapor por US$ 10.000;
   - `Cost_Benefit_Score`: desempenho por US$ 10.000.
3. **Análise exploratória**: estatísticas descritivas e matriz de correlação de Pearson.
4. **Inferência estatística**: intervalos de confiança de 95% do custo-benefício médio por região.
5. **Testes de hipóteses** (teste t de Welch):
   - HP por US$ 10k: EUA vs Europa;
   - aceleração 0-60 mph: eletrificados vs combustão.
6. **Regressão linear (OLS)**:
   - simples: preço em função do `Performance_Score`;
   - múltipla: preço em função de potência, torque e aceleração;
   - diagnóstico de multicolinearidade (VIF) e análise de resíduos.
7. **Ranking** dos 10 supercarros com melhor custo-benefício.

---

## 📊 Principais conclusões

- Montadoras americanas entregam, em média, **mais cavalos-vapor por dólar** que as europeias (p < 0,001).
- Veículos eletrificados (híbridos e elétricos) têm **aceleração inicial significativamente superior** à da combustão pura.
- O modelo de regressão múltipla (R² > 0,60) indica que a precificação segue uma **forte lógica técnica**.

**Limitações:** o estudo não considera dados aerodinâmicos, peso total nem tempos de volta em pista.

---

## 🛠️ Tecnologias

- Python (notebook de análise + `app.py` do dashboard)
- pandas e NumPy
- SciPy e statsmodels
- Matplotlib e Seaborn
- Google Colab / Jupyter Notebook