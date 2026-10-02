import re
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

def clean_data():
    raw_path = 'C:/Users/foxcr/.gemini/antigravity/scratch/supercar_dashboard/raw_supercars.csv'
    df = pd.read_csv(raw_path)
    
    df = df.drop_duplicates().reset_index(drop=True)
    
    # Clean Price
    def clean_price(val):
        if pd.isna(val):
            return np.nan
        val_str = str(val).replace('$', '').replace(',', '').replace('"', '').strip()
        try:
            return float(val_str)
        except:
            return np.nan
            
    df['Price_USD'] = df['Price (in USD)'].apply(clean_price)
    
    # Clean 0-60 Time
    def clean_accel(val):
        if pd.isna(val):
            return np.nan
        val_str = str(val).replace('<', '').replace('s', '').strip()
        try:
            return float(val_str)
        except:
            return np.nan
            
    df['0_60_Time_s'] = df['0-60 MPH Time (seconds)'].apply(clean_accel)
    
    # Clean Horsepower
    def clean_hp(row):
        val = row['Horsepower']
        model = str(row['Car Model'])
        make = str(row['Car Make'])
        if pd.isna(val):
            return np.nan
        val_str = str(val).replace('+', '').replace(',', '').strip()
        try:
            num = float(val_str)
            if num > 3000:
                if 'Roadster' in model or 'Tesla' in make:
                    return 1020.0
            return num
        except:
            return np.nan

    df['Horsepower_clean'] = df.apply(clean_hp, axis=1)
    
    # Clean Torque
    def clean_torque(row):
        val = row['Torque (lb-ft)']
        model = str(row['Car Model'])
        make = str(row['Car Make'])
        if pd.isna(val) or str(val).strip() in ['-', 'N/A']:
            if 'Roadster' in model:
                return 737.0
            return np.nan
        val_str = str(val).replace('+', '').replace(',', '').strip()
        try:
            num = float(val_str)
            if num > 3000:
                if 'Roadster' in model or 'Tesla' in make:
                    return 737.0
            return num
        except:
            return np.nan

    df['Torque_clean'] = df.apply(clean_torque, axis=1)
    
    # Powertrain & Engine Size
    def clean_engine(val):
        val_str = str(val).strip()
        if any(term in val_str.lower() for term in ['electric', 'tri-motor', 'kwh']) or val_str in ['0', 'N/A', '-', 'nan']:
            return 'Elétrico', 0.0
        elif 'hybrid' in val_str.lower() or '+' in val_str:
            num_match = re.search(r'(\d+\.?\d*)', val_str)
            size = float(num_match.group(1)) if num_match else 3.0
            return 'Híbrido', size
        else:
            try:
                size = float(val_str)
                return 'Combustão', size
            except:
                return 'Combustão', 4.0

    engine_res = df['Engine Size (L)'].apply(clean_engine)
    df['Powertrain'] = [r[0] for r in engine_res]
    df['Engine_Displacement_L'] = [r[1] for r in engine_res]
    
    # Impute missing torque/hp by model if any
    for col in ['Horsepower_clean', 'Torque_clean', '0_60_Time_s', 'Price_USD']:
        df[col] = df.groupby(['Car Make', 'Car Model'])[col].transform(lambda s: s.fillna(s.median()))
        df[col] = df[col].fillna(df[col].median())
        
    # Origin Region Mapping
    us_makes = ['Chevrolet', 'Ford', 'Dodge', 'Tesla', 'Shelby']
    asia_makes = ['Nissan', 'Lexus', 'Toyota', 'Acura', 'Mazda', 'Subaru', 'Kia']
    def get_origin(make):
        if make in us_makes:
            return 'Estados Unidos'
        elif make in asia_makes:
            return 'Ásia'
        elif make == 'W Motors':
            return 'Oriente Médio'
        else:
            return 'Europa'
            
    df['Origin_Region'] = df['Car Make'].apply(get_origin)
    
    # Feature Engineering (Metrics)
    df['HP_per_10k_USD'] = (df['Horsepower_clean'] / (df['Price_USD'] / 10000.0)).round(2)
    df['Torque_per_10k_USD'] = (df['Torque_clean'] / (df['Price_USD'] / 10000.0)).round(2)
    
    # Smartphone-style Benchmark Score (0 to 100)
    # Hardware metrics: HP (40%), Torque (30%), Acceleration (30%)
    hp_norm = (df['Horsepower_clean'] - df['Horsepower_clean'].min()) / (df['Horsepower_clean'].max() - df['Horsepower_clean'].min())
    torque_norm = (df['Torque_clean'] - df['Torque_clean'].min()) / (df['Torque_clean'].max() - df['Torque_clean'].min())
    accel_norm = (df['0_60_Time_s'].max() - df['0_60_Time_s']) / (df['0_60_Time_s'].max() - df['0_60_Time_s'].min())
    
    df['Performance_Score'] = (100 * (0.40 * hp_norm + 0.30 * torque_norm + 0.30 * accel_norm)).round(2)
    
    # Cost-Benefit Ratio / Value Score (Score per 10k USD)
    df['Cost_Benefit_Score'] = (df['Performance_Score'] / (df['Price_USD'] / 10000.0)).round(2)
    
    # Econometric / Statistical Modeling: Linear Regression for Theoretical Price
    # Using log(Price) vs Performance metrics to handle skewness and multiplicative luxury premiums
    X = sm.add_constant(df[['Horsepower_clean', 'Torque_clean', '0_60_Time_s']])
    model_lin = sm.OLS(df['Price_USD'], X).fit()
    df['Estimated_Price_Linear'] = model_lin.predict(X).round(2)
    df['Residual_Linear'] = (df['Price_USD'] - df['Estimated_Price_Linear']).round(2)
    
    # Log model provides better realistic fit for hypercars
    y_log = np.log(df['Price_USD'])
    model_log = sm.OLS(y_log, X).fit()
    df['Estimated_Price_Log'] = np.exp(model_log.predict(X)).round(2)
    df['Residual_Log'] = (df['Price_USD'] - df['Estimated_Price_Log']).round(2)
    df['Price_Diff_Pct'] = (((df['Price_USD'] - df['Estimated_Price_Log']) / df['Estimated_Price_Log']) * 100).round(1)
    
    def classify_cb(pct):
        if pct <= -30:
            return 'Custo-Benefício Excepcional'
        elif pct < 0:
            return 'Bom Custo-Benefício'
        elif pct <= 50:
            return 'Preço Compatível com Mercado'
        else:
            return 'Prêmio de Exclusividade / Grife'
            
    df['Classification_CB'] = df['Price_Diff_Pct'].apply(classify_cb)
    
    output_path = 'C:/Users/foxcr/.gemini/antigravity/scratch/supercar_dashboard/supercars_clean.csv'
    df.to_csv(output_path, index=False)
    print(f'Clean data saved to {output_path}. Shape: {df.shape}')
    print('\nModel Performance:')
    print(f'Linear Model R^2: {model_lin.rsquared:.4f}')
    print(f'Log-Linear Model R^2: {model_log.rsquared:.4f}')
    
if __name__ == '__main__':
    clean_data()
