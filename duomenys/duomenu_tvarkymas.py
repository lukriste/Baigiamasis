import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import re

def prisijungti_prie_db():
    engine = create_engine("mysql+pymysql://lukriste:Astikiusavimi100@localhost/gnm")
    return engine


def nuskaityti_duomenis(engine):
    df = pd.read_sql("SELECT * FROM simptomai", con=engine)
    return df

def isvalyti_sinonimus(tekstas):
    if pd.isna(tekstas):
        return []
    return [s.strip().lower() for s in tekstas.replace(";", ",").split(",") if s.strip()]

def kurti_sinonimu_zemelapi(df):
    sinonimu_zemelapis = {}
    for _, row in df.iterrows():
        pagrindinis = row["simptomas"].strip().lower()
        sinonimai = isvalyti_sinonimus(row["sinonimai"])
        for sinonimas in sinonimai:
            sinonimu_zemelapis[sinonimas] = pagrindinis
    return sinonimu_zemelapis


df = pd.read_sql("SELECT GNM_konfliktas FROM simptomai", con=prisijungti_prie_db())
pasiskirstymas = df["GNM_konfliktas"].value_counts()

for konfliktas in df["GNM_konfliktas"].unique():
    print("-", konfliktas)

def grupuoti_konflikta(tekstas):
    if pd.isna(tekstas):
        return "Nežinomas"

    tekstas = tekstas.lower()

    # Kūno „kąsnio“ konfliktas
    if re.search(r"(kąsni|neviršk|praryt|saldum|nuoding|atsikrat|apdoroj|nepavyk|kūn|apsinuodij|maist|skon)", tekstas):
        return "Kūno 'kąsnio' konfliktas"

    # Savigarbos sumažėjimo konfliktas
    if re.search(r"(savigarb|savivert|nuvertin|nepakankam|nevert|nesugeb|nepajėg|bevert|vert|išnykim|nematom|neverting)", tekstas):
        return "Savigarbos sumažėjimo konfliktas"
    
    if re.search(r"(savigarb|savivert|nuvertin|nepakankam|nevert|nesugeb|nepajėg|bevert)", tekstas):
        return "Savigarbos sumažėjimo konfliktas"
    


    # Streso konfliktas
    if re.search(r"(laiko trūk|spaudimas|stres|ekstrem|suspėt|greitis)", tekstas):
        return "Streso / greičio / spaudimo konfliktas"

    # Išsiskyrimo konfliktas
    if re.search(r"(išsiskyr|atskyr|netekt|palik|atstūm|išėj|prarad|vieniš|atsiskyr|izoliacij)", tekstas):
        return "Išsiskyrimo konfliktas"

    # Mirties baimės konfliktas
    if re.search(r"(mirt|uždus|kvėpav|gyvyb|baim|dūst|deguon)", tekstas):
        return "Mirties baimės konfliktas"

    # Seksualinis konfliktas
    if re.search(r"(seksual|intym|pažemin|lytin|santyk|žindym|geidul|genit)", tekstas):
        return "Seksualinis konfliktas"

    # Estetinis konfliktas
    if re.search(r"(išvaizd|estet|žaves|grož|nepatrauk)", tekstas):
        return "Estetinis konfliktas"

    # Bėglio konfliktas
    if re.search(r"(bėgl|bėg|pabėg|negalėjim.*pabėg|bėgau|nepabėg|egzistenc)", tekstas):
        return "Bėglio konfliktas"
    
    # Užsitęsę gijimo procesai / recidyvai
    if re.search(r"(gijimo faz|gijim|gyjimo|gijimas|gyjim|gijimo rezultatas)", tekstas):
        return "Gijimo fazės / gijimo procesai"

    # Motorinis konfliktas
    if re.search(r"(motorin|judėjim|negalėjim.*jud|negalėjim.*veik|nepajėg.*vaikšč|negalėjim.*ženg)", tekstas):
        return "Motorinis konfliktas"
    
    #Šeimos /santykių konfliktas
    if re.search(r"(motin|tėv|šeim|vaik|partner|sutuoktin|močiut|protėvi|gimin)", tekstas):
        return "Šeimos / santykių konfliktas"

    # Sensorinis konfliktas
    if re.search(r"(gird|nejautr|jutim|pojūt|klausy|svaig|neišgirst|nebegal.*gird|matyt|žiūr|nematyt|švies|vaizd|regėj|konjungty|reg|klausym|triukš|negird|vizual)", tekstas):
        return "Sensorinis / regos / klausos konfliktas"
    
    if re.search(r"(kvap|užuost|pojūtis|nemalonaus pojūčio)", tekstas):
        return "Kvapo / jutiminis konfliktas"
    
    if re.search(r"(atak|smūg|apsaug|smūgi|invazij|smurt)", tekstas):
        return "Atakos / apsaugos konfliktas"


    if re.search(r"(kontrol|priverstin|nurodym|paklusim|spaust|tvark|rūpesč|glob|pasirūp|priežiūr|atsakomyb|pareig)", tekstas):
        return "Kontrolės / rūpesčio konfliktas"

    # Kombinuotas konfliktas
    if re.search(r"(dvigub|kombinuot|konsteliacij|derin|mišr|tarp dviej)", tekstas):
        return "Kombinuotas konfliktas"

    return "Kiti"

df["GNM_konf_grup"] = df["GNM_konfliktas"].apply(grupuoti_konflikta)

print(df["GNM_konf_grup"].value_counts())

def generuoti_bar_grafika(df):
    df["GNM_konf_grup"] = df["GNM_konfliktas"].apply(grupuoti_konflikta)
    pasiskirstymas = df["GNM_konf_grup"].value_counts()
    plt.figure(figsize=(12, 6))
    plt.bar(pasiskirstymas.index, pasiskirstymas.values)
    plt.xticks(rotation=45, ha='right')
    plt.title("GNM konfliktų grupių pasiskirstymas")
    plt.ylabel("Įeraišų kiekis")
    plt.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.savefig("grafikai/konfliktu_pasiskirstymas.png", dpi=300)
    plt.close()

if __name__ == "__main__":
    engine = prisijungti_prie_db()
    df = nuskaityti_duomenis(engine)
    sinonimu_zemelapis = kurti_sinonimu_zemelapi(df)
    generuoti_bar_grafika(df)

kiti_df = df[df["GNM_konf_grup"] == "Kiti"]
for tekstas in kiti_df["GNM_konfliktas"]:
    print("-", tekstas)
    




