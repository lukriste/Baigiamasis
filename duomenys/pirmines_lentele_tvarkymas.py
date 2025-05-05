import pandas as pd
from sqlalchemy import create_engine
import re

#Sutvarkau lentele

failo_kelias = r"C:\Users\Kristina\Desktop\Mokslai\PROGRAMAVIMAS\Baigiamasis\Baigiamasis\duomenys\gnm_simptomai.xlsx"

df = pd.read_excel(failo_kelias)

df = df[['simptomas', 'sinonimai', 'GNM_konfliktas', 'GNM_pavyzdys', 'GNM_papildomapastaba']]


def normalizuoti_teksta(tekstas):
    if pd.isna(tekstas):
        return tekstas
    tekstas = tekstas.strip()
    tekstas = tekstas.replace("“", '"').replace("”", '"').replace("„", '"')
    tekstas = tekstas.replace("‘", "'").replace("’", "'")
    tekstas = tekstas.replace("–", "-").replace("—", "-")
    tekstas = tekstas.replace("\\", "/")
    tekstas = re.sub(r"[\r\n\t]", " ", tekstas)
    tekstas = re.sub(r"\s{2,}", " ", tekstas)
    tekstas = re.sub(r"\s+([.,;!?()])", r"\1", tekstas)
    return tekstas

def sutvarkyti_sinonimus(tekstas):
    if pd.isna(tekstas):
        return tekstas
    tekstas = "; ".join([s.strip() for s in tekstas.split(",")])
    return normalizuoti_teksta(tekstas)

df["sinonimai"] = df["sinonimai"].apply(sutvarkyti_sinonimus)

for s in ["GNM_konfliktas", "GNM_pavyzdys", "GNM_papildomapastaba"]:
    df[s] = df[s].apply(normalizuoti_teksta)


#Ikeliu lentele i mysql

engine = create_engine("mysql+pymysql://lukriste:Astikiusavimi100@localhost/gnm")
df.to_sql(name='simptomai', con=engine, if_exists='replace', index=False) #kadangi jau buvo tai ikeliu naujai ant virsaus




