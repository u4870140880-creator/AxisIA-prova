import io
import re
import zipfile
import requests
import streamlit as st

st.set_page_config(
    page_title="AXIS Technical Support", page_icon="⚡", layout="centered"
)

st.title("⚡ AXIS Technical Support")
st.caption("Engineered with DeepSeek-V3 for Fiverr Automation")

# Input principali
api_key = st.text_input(
    "DeepSeek API Key:", type="password", help="Inserisci la tua sk-..."
)
richiesta_cliente = st.text_area(
    "Richiesta del cliente Fiverr:",
    height=180,
    placeholder="Incolla qui i requisiti del cliente...",
)

col1, col2 = st.columns(2)
with col1:
  nome_progetto = st.text_input("Nome Progetto:", "Progetto_AXIS")
with col2:
  lingua = st.selectbox(
      "Lingua Messaggio:", ["Inglese", "Italiano"], index=0
  )

if st.button("🚀 Genera Pacchetto Consegna", type="primary"):
  if not api_key:
    st.error("Inserisci la tua API Key di DeepSeek!")
  elif not richiesta_cliente:
    st.error("Incolla la richiesta del cliente!")
  else:
    with st.spinner("DeepSeek-V3 sta elaborando il codice e il pacchetto..."):

      system_prompt = f"""
            Sei un ingegnere del software ed esperto di elettronica ed embedded systems per AXIS Technical Support.
            Il tuo compito è generare codice impeccabile in C++, Arduino o Python basandoti sulla richiesta del cliente.

            Rispondi SEMPRE e TASSATIVAMENTE strutturando la risposta in queste 4 sezioni esatte:

            ---SEZIONE 1: CODICE SORGENTE---
            - Codice completo, pulito e commentato riga per riga.
            - Includi tutte le librerie necessarie (#include o import).
            - Nessun segnaposto, nessun TODO, il codice deve essere pronto all'uso.

            ---SEZIONE 2: SCHEMA DEI COLLEGAMENTI (PINOUT)---
            - Lista/Tabella dettagliata dei pin e componenti hardware da collegare.

            ---SEZIONE 3: MANUALE DI CARICAMENTO RAPIDO---
            - Guida passo-passo in 3 punti per compilare e caricare il codice.
            - Elenco esatto delle librerie da installare nell'IDE/ambiente.

            ---SEZIONE 4: MESSAGGIO DI CONSEGNA CLIENTE---
            - Messaggio cortese e professionale per il cliente in lingua {lingua}.
            - Firma obbligatoria: "AXIS Technical Support".
            """

      headers = {
          "Authorization": f"Bearer {api_key}",
          "Content-Type": "application/json",
      }

      payload = {
          "model": "deepseek-chat",
          "messages": [
              {"role": "system", "content": system_prompt},
              {"role": "user", "content": richiesta_cliente},
          ],
          "temperature": 0.2,
      }

      try:
        res = requests.post(
            "https://api.deepseek.com/chat/completions",
            json=payload,
            headers=headers,
        )
        data = res.json()
        testo = data["choices"][0]["message"]["content"]

        # Estrazione delle sezioni
        sez1 = (
            testo.split("---SEZIONE 1: CODICE SORGENTE---")[1]
            .split("---SEZIONE 2:")[0]
            .strip()
        )
        sez2 = (
            testo.split("---SEZIONE 2: SCHEMA DEI COLLEGAMENTI (PINOUT)---")[1]
            .split("---SEZIONE 3:")[0]
            .strip()
        )
        sez3 = (
            testo.split("---SEZIONE 3: MANUALE DI CARICAMENTO RAPIDO---")[1]
            .split("---SEZIONE 4:")[0]
            .strip()
        )
        sez4 = testo.split(
            "---SEZIONE 4: MESSAGGIO DI CONSEGNA CLIENTE---"
        )[1].strip()

        # Pulizia blocchi markdown dal codice
        codice_clean = re.sub(
            r"^```cpp|^```ino|^```python|^```|\n```$",
            "",
            sez1,
            flags=re.MULTILINE,
        ).strip()

        # Riconoscimento formato file
        estensione = ".ino"
        if "import " in codice_clean or "def " in codice_clean:
          estensione = ".py"
        elif "int main(" in codice_clean:
          estensione = ".cpp"

        # Creazione pacchetto .ZIP in memoria
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(
            zip_buffer, "w", zipfile.ZIP_DEFLATED
        ) as zip_file:
          # File codice
          zip_file.writestr(
              f"{nome_progetto}/{nome_progetto}{estensione}", codice_clean
          )
          # File Guida e Pinout
          zip_file.writestr(
              "PINOUT_E_GUIDA.md",
              f"# Documentazione Progetto\n\n## Collegamenti Hardware\n{sez2}\n\n## Guida al Caricamento\n{sez3}",
          )
          # File Messaggio Consegna
          zip_file.writestr("MESSAGGIO_CLIENTE.txt", sez4)

        st.success("✅ Pacchetto generato con successo!")

        # Download ZIP
        st.download_button(
            label="📦 Scarica File .ZIP Pronto",
            data=zip_buffer.getvalue(),
            file_name=f"{nome_progetto}_AXIS.zip",
            mime="application/zip",
            use_container_width=True,
        )

        st.subheader("Messaggio di consegna pronto per Fiverr:")
        st.code(sez4, language="text")

      except Exception as e:
        st.error(f"Errore durante l'elaborazione: {e}")
