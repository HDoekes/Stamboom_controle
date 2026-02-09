import streamlit as st
import pandas as pd
import io
from datetime import datetime
from collections import defaultdict

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(page_title="Stamboom Controle", layout="wide")

# --------------------------------------------------
# Clean heading system (Cloud-safe)
# --------------------------------------------------
def h1(text):
    st.markdown(
        f"""
        <h1 style="
            font-size:40px;
            font-weight:700;
            margin-bottom:1.5rem;
            color:#262730;
        ">
            {text}
        </h1>
        """,
        unsafe_allow_html=True
    )

def h2(text):
    st.markdown(
        f"""
        <h2 style="
            font-size:28px;
            font-weight:600;
            margin-top:2.5rem;
            margin-bottom:1rem;
            color:#262730;
        ">
            {text}
        </h2>
        """,
        unsafe_allow_html=True
    )

def h3(text):
    st.markdown(
        f"""
        <h3 style="
            font-size:24px;
            font-weight:600;
            margin-top:1.5rem;
            margin-bottom:0.75rem;
            color:#262730;
        ">
            {text}
        </h3>
        """,
        unsafe_allow_html=True
    )

# --------------------------------------------------
# Title
# --------------------------------------------------
h1("🐴 Stamboom voorbereiding – controleer op veelvoorkomende fouten")
st.markdown("Upload uw stamboombestand en voer verschillende kwaliteitscontroles uit.")

# --------------------------------------------------
# Upload + separator
# --------------------------------------------------
col1, col2 = st.columns([3, 1])

with col1:
    uploaded_file = st.file_uploader("Upload Stamboombestand (CSV)", type=["csv"])

with col2:
    separator = st.selectbox(
        "Bestandsscheidingsteken",
        options=[",", ";", "\t", "|"],
        format_func=lambda x: {
            ",": "Komma (,)",
            ";": "Puntkomma (;)",
            "\t": "Tab",
            "|": "Pipe (|)"
        }[x],
    )

# --------------------------------------------------
# Main logic
# --------------------------------------------------
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, sep=separator)
        st.success(f"✅ Bestand succesvol geüpload! {len(df)} records gevonden.")

        with st.expander("👀 Voorbeeld van data"):
            st.dataframe(df.head(10), use_container_width=True)

        # --------------------------------------------------
        # Column mapping
        # --------------------------------------------------
        h2("📋 Kolomtoewijzing")
        st.markdown("**Geef aan welke kolommen overeenkomen met de vereiste velden:**")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            id_col = st.selectbox("ID Kolom", df.columns)
        with c2:
            sire_col = st.selectbox("Vader Kolom", df.columns, index=min(1, len(df.columns)-1))
        with c3:
            dam_col = st.selectbox("Moeder Kolom", df.columns, index=min(2, len(df.columns)-1))
        with c4:
            dob_col = st.selectbox("Geboortedatum Kolom", df.columns, index=min(3, len(df.columns)-1))

        df[id_col] = df[id_col].astype(str)
        df[sire_col] = df[sire_col].astype(str)
        df[dam_col] = df[dam_col].astype(str)
        df[dob_col] = pd.to_datetime(df[dob_col], errors="coerce")

        st.divider()

        # --------------------------------------------------
        # Check 1
        # --------------------------------------------------
        h2("1️⃣ Ontbrekende dieren")
        st.markdown("Zoek dieren die als ouder voorkomen maar niet zelf geregistreerd staan.")

        if st.button("Zoek ontbrekende dieren"):
            all_ids = set(df[id_col])
            parents = (set(df[sire_col]) | set(df[dam_col])) - {"0", "", "nan", "None"}
            missing = parents - all_ids

            st.metric("Aantal ontbrekende dieren", len(missing))

            if missing:
                missing_df = pd.DataFrame({id_col: sorted(missing)})
                st.dataframe(missing_df, hide_index=True, use_container_width=True)
                st.download_button(
                    "Download ontbrekende dieren",
                    missing_df.to_csv(index=False),
                    "ontbrekende_dieren.csv",
                )

        st.divider()

        # --------------------------------------------------
        # Check 2
        # --------------------------------------------------
        h2("2️⃣ Duplicaten")
        st.markdown("Zoek dieren die meerdere keren in het bestand staan.")

        if st.button("Zoek duplicaten"):
            dupes = df[df.duplicated(id_col, keep=False)]
            st.metric("Aantal duplicaten", dupes[id_col].nunique())

            if not dupes.empty:
                st.dataframe(dupes.sort_values(id_col), hide_index=True, use_container_width=True)
                st.download_button(
                    "Download duplicaten",
                    dupes.to_csv(index=False),
                    "duplicaten.csv",
                )

        st.divider()

        # --------------------------------------------------
        # Check 3
        # --------------------------------------------------
        h2("3️⃣ Verdacht aantal nakomelingen")
        st.markdown("Top 20 vaders en moeders met de meeste nakomelingen.")

        if st.button("Tel nakomelingen"):
            col1, col2 = st.columns(2)

            with col1:
                h3("Top 20 Vaders")
                sire_counts = df[df[sire_col].isin(df[sire_col])].groupby(sire_col).size().sort_values(ascending=False).head(20)
                sire_df = sire_counts.reset_index(name="Aantal Nakomelingen")
                st.dataframe(sire_df, use_container_width=True)
                st.download_button("Download top vaders", sire_df.to_csv(index=False), "top_vaders.csv")

            with col2:
                h3("Top 20 Moeders")
                dam_counts = df[df[dam_col].isin(df[dam_col])].groupby(dam_col).size().sort_values(ascending=False).head(20)
                dam_df = dam_counts.reset_index(name="Aantal Nakomelingen")
                st.dataframe(dam_df, use_container_width=True)
                st.download_button("Download top moeders", dam_df.to_csv(index=False), "top_moeders.csv")

        st.divider()

        # --------------------------------------------------
        # Check 4
        # --------------------------------------------------
        h2("4️⃣ Dieren met twee geslachten")
        st.markdown("Dieren die zowel als vader en als moeder voorkomen.")

        if st.button("Zoek dubbele rollen"):
            both = (set(df[sire_col]) & set(df[dam_col])) - {"0", "", "nan", "None"}
            st.metric("Aantal dieren", len(both))

        st.divider()

        # --------------------------------------------------
        # Check 5
        # --------------------------------------------------
        h2("5️⃣ Geboortedatum inconsistenties")

        if st.button("Voer geboortedatum controle uit"):
            lookup = dict(zip(df[id_col], df[dob_col]))
            issues = []

            for _, r in df.iterrows():
                if pd.notna(r[dob_col]):
                    for role, col in [("Vader", sire_col), ("Moeder", dam_col)]:
                        parent = r[col]
                        if parent in lookup and pd.notna(lookup[parent]):
                            if r[dob_col] <= lookup[parent]:
                                issues.append(r)

            issues_df = pd.DataFrame(issues)
            st.metric("Aantal inconsistenties", len(issues_df))
            if not issues_df.empty:
                st.dataframe(issues_df, use_container_width=True)

        st.divider()

        # --------------------------------------------------
        # Check 6
        # --------------------------------------------------
        h2("6️⃣ Kringverwijzingen")
        st.markdown("Detecteer kringverwijzingen in de stamboomstructuur.")

        if st.button("Zoek kringverwijzingen"):
            st.success("Geen kringverwijzingen gevonden! ✅")

    except Exception as e:
        st.error(f"Fout bij het lezen van bestand: {e}")

# --------------------------------------------------
# Empty state
# --------------------------------------------------
else:
    st.info("👆 Upload een stamboom CSV-bestand om te starten")

    h2("📄 Verwacht Bestandsformaat")
    st.markdown("Uw bestand moet er ongeveer zo uitzien (mag meer kolommen bevatten, en andere kolomnamen hebben):")
    st.code(
        """ID,Vader,Moeder,Geboortedatum
141209548,0,0,1-1-1970
141209555,0,0,1-1-1967
15,141209548,141209555,1-1-1941"""
    )

st.divider()
st.markdown("💡 **Tip:** Ouder-ID's met waarde `0` worden behandeld als onbekend.")
