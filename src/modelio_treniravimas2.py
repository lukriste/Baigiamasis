import pandas as pd
import re
from sqlalchemy import create_engine
from transformers import T5Tokenizer, T5Config, TFAutoModelForSeq2SeqLM, DataCollatorForSeq2Seq
from datasets import Dataset
from sklearn.model_selection import train_test_split
import tensorflow as tf
import matplotlib.pyplot as plt



engine = create_engine("mysql+pymysql://lukriste:Astikiusavimi100@localhost/gnm1")
df = pd.read_sql("SELECT ivestis , isvestis FROM simptomai", con=engine)

train_df, test_df = train_test_split(df, test_size=0.1, random_state=42)

train_dataset = Dataset.from_pandas(train_df)
test_dataset = Dataset.from_pandas(test_df)

tokenizer = T5Tokenizer.from_pretrained("t5-small")

def tokenize_function(example):
    input_enc = tokenizer(example["ivestis"], padding="max_length", truncation=True, max_length=128)
    output_enc = tokenizer(example["isvestis"], padding="max_length", truncation=True, max_length=128)
    input_enc["labels"] = output_enc["input_ids"]
    return input_enc

train_tokenized = train_dataset.map(tokenize_function, batched=False)
test_tokenized = test_dataset.map(tokenize_function, batched=False)

model = TFAutoModelForSeq2SeqLM.from_pretrained("t5-small")

train_set = train_tokenized.to_tf_dataset(
    columns=["input_ids", "attention_mask"],
    label_cols=["labels"],
    shuffle=True,
    batch_size=8,
)

val_set = test_tokenized.to_tf_dataset(
    columns=["input_ids", "attention_mask"],
    label_cols=["labels"],
    shuffle=False,
    batch_size=8,
)

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=5e-5))

model.fit(train_set, validation_data=val_set, epochs=3)

model.save_pretrained("gnm-t5")
tokenizer.save_pretrained("gnm-t5")

data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model, return_tensors="tf")

print("\n🧪 Testuojame modelį su keliomis ivestimis:\n")
for i in range(3):
    tekstas = test_df.iloc[i]["ivestis"]
    tikras = test_df.iloc[i]["isvestis"]
    input_ids = tokenizer(tekstas, return_tensors="tf", truncation=True, padding=True).input_ids
    output_ids = model.generate(input_ids, max_length=128)
    sugeneruota = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    
    print(f"🔹 Įvestis: {tekstas}")
    print(f"✅ Tikras atsakymas: {tikras}")
    print(f"🧠 Modelio atsakymas: {sugeneruota}\n")

history = model.fit(train_set, validation_data=val_set, epochs=3)


plt.plot(history.history["loss"], label="Train Loss")
plt.plot(history.history["val_loss"], label="Validation Loss")
plt.legend()
plt.title("T5 treniravimo kreivė")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.show()