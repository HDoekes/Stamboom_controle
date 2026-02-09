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
        st.markdown("Zoek dieren die als vader en als moeder in de stamboom staan.")
        
        if st.button("Zoek dieren die zowel vader en moeder zijn", key="check4"):
            # Get animals that appear as both sire and dam
            sires = set(df[sire_col].unique()) - {'0', '', 'nan', 'None'}
            dams = set(df[dam_col].unique()) - {'0', '', 'nan', 'None'}
            both_roles = sires & dams
            
            st.metric("Aantal dieren die vader en moeder zijn.", len(both_roles))
            
            if len(both_roles) > 0:
                # Create Excel file with sheets per ID
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    for animal_id in sorted(both_roles):
                        # Get records where this animal is sire or dam
                        records = df[(df[sire_col] == animal_id) | (df[dam_col] == animal_id)]
                        # Limit sheet name to 31 characters (Excel limitation)
                        sheet_name = str(animal_id)[:31]
                        records.to_excel(writer, sheet_name=sheet_name, index=False)
                
                output.seek(0)
                
                st.success(f"Excel bestand aangemaakt met {len(both_roles)} tabbladen")
                st.download_button(
                    label="Download Excel Bestand",
                    data=output,
                    file_name="dubbele_rol_dieren.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download4"
                )
        
        st.divider()

        # --------------------------------------------------
        # Check 5
        # --------------------------------------------------
        h2("5️⃣ Geboortedatum inconsistenties")
        st.markdown("Zoek dieren die geboren zijn voor hun ouders. Let wel: vaak zijn dit dieren waarvan de geboortedatum eigenlijk onbekend was, en die bijv. op 1-1-1900 zijn gezet. Let op dat deze niet worden meegenomen in het berekenen van het generatieinterval. Voor andere inconsitenties, kan het zijn dat de afstamming niet klopt, of dat de geboortedatum van de nakomeling of het ouderdier niet klopt.")
        
        if st.button("Controleer geboortedata", key="check5"):
            # Create a date lookup
            date_lookup = dict(zip(df[id_col], df[dob_col]))
            
            inconsistency_data = []
            
            for idx, row in df.iterrows():
                animal_id = row[id_col]
                animal_dob = row[dob_col]
                sire_id = row[sire_col]
                dam_id = row[dam_col]
                
                if pd.notna(animal_dob):
                    problems = []
                    sire_dob = None
                    dam_dob = None
                    
                    # Check sire
                    if sire_id in date_lookup and sire_id not in ['0', '', 'nan']:
                        sire_dob = date_lookup[sire_id]
                        if pd.notna(sire_dob) and animal_dob <= sire_dob:
                            problems.append('vader')
                    
                    # Check dam
                    if dam_id in date_lookup and dam_id not in ['0', '', 'nan']:
                        dam_dob = date_lookup[dam_id]
                        if pd.notna(dam_dob) and animal_dob <= dam_dob:
                            problems.append('moeder')
                    
                    if problems:
                        inconsistency_data.append({
                            'Dier_ID': animal_id,
                            'Geboortedatum_Dier': animal_dob.strftime('%d-%m-%Y') if pd.notna(animal_dob) else '',
                            'Vader_ID': sire_id if sire_id not in ['0', '', 'nan'] else '',
                            'Geboortedatum_Vader': sire_dob.strftime('%d-%m-%Y') if pd.notna(sire_dob) else '',
                            'Moeder_ID': dam_id if dam_id not in ['0', '', 'nan'] else '',
                            'Geboortedatum_Moeder': dam_dob.strftime('%d-%m-%Y') if pd.notna(dam_dob) else '',
                            'Probleem_bij': ', '.join(problems)
                        })
            
            st.metric("Aantal datum inconsistenties", len(inconsistency_data))
            
            if len(inconsistency_data) > 0:
                inconsistent_df = pd.DataFrame(inconsistency_data)
                st.dataframe(inconsistent_df, hide_index=True, use_container_width=True)
                
                csv = inconsistent_df.to_csv(index=False)
                st.download_button(
                    label="Download inconsistente records",
                    data=csv,
                    file_name="geboortedatum_inconsistenties.csv",
                    mime="text/csv",
                    key="download5"
                )
        
        st.divider()

        # --------------------------------------------------
        # Check 6
        # --------------------------------------------------
        h2("6️⃣ Kringverwijzingen")
        st.markdown("Detecteer kringverwijzingen in de stamboomstructuur")
        
        if st.button("Zoek kringverwijzingen", key="check6"):
            def find_circular_references(df, id_col, sire_col, dam_col):
                """Find circular references in pedigree"""
                # Build parent dictionary
                parents = {}
                for _, row in df.iterrows():
                    animal_id = str(row[id_col])
                    sire = str(row[sire_col])
                    dam = str(row[dam_col])
                    
                    parent_list = []
                    if sire not in ['0', '', 'nan', 'None']:
                        parent_list.append(sire)
                    if dam not in ['0', '', 'nan', 'None']:
                        parent_list.append(dam)
                    
                    if parent_list:
                        parents[animal_id] = parent_list
                
                # Find circular references using DFS
                circular_refs = []
                
                def has_cycle(node, visited, rec_stack, path):
                    visited.add(node)
                    rec_stack.add(node)
                    path.append(node)
                    
                    if node in parents:
                        for parent in parents[node]:
                            if parent not in visited:
                                if has_cycle(parent, visited, rec_stack, path):
                                    return True
                            elif parent in rec_stack:
                                # Found a cycle
                                cycle_start = path.index(parent)
                                cycle = path[cycle_start:] + [parent]
                                circular_refs.append(cycle)
                                return True
                    
                    path.pop()
                    rec_stack.remove(node)
                    return False
                
                visited = set()
                for node in parents.keys():
                    if node not in visited:
                        has_cycle(node, visited, set(), [])
                
                return circular_refs
            
            circular_refs = find_circular_references(df, id_col, sire_col, dam_col)
            
            if len(circular_refs) > 0:
                st.error(f"⚠️ {len(circular_refs)} kringverwijzing(en) gevonden!")
                st.markdown("---")
                
                for i, cycle in enumerate(circular_refs, 1):
                    st.markdown(f"### Kringverwijzing {i}")
                    st.markdown(f"**Pad:** `{' → '.join(cycle)}`")
                    st.markdown("---")
                
                # Create downloadable report
                report_lines = []
                for i, cycle in enumerate(circular_refs, 1):
                    report_lines.append(f"Kringverwijzing {i}: {' → '.join(cycle)}")
                
                report_text = '\n'.join(report_lines)
                st.download_button(
                    label="Download kringverwijzingen rapport",
                    data=report_text,
                    file_name="kringverwijzingen.txt",
                    mime="text/plain",
                    key="download6"
                )
            else:
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
