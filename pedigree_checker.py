import streamlit as st
import pandas as pd
import io
import zipfile
from datetime import datetime
from collections import defaultdict

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(page_title="Pedigree Checker", layout="wide")

# --------------------------------------------------
# Language selection
# --------------------------------------------------
col_left, col_right = st.columns([8, 1])
with col_right:
    language = st.selectbox(
        "🌐",
        options=["NL", "EN"],
        label_visibility="collapsed"
    )

# --------------------------------------------------
# Translations
# --------------------------------------------------
TRANSLATIONS = {
    "NL": {
        "title": "🐴 Stamboom opschonen: check veelvoorkomende fouten",
        "subtitle": "Upload uw stamboombestand en voer verschillende controles uit.",
        "upload": "Upload Stamboombestand (CSV)",
        "separator": "Bestandsscheidingsteken",
        "comma": "Komma (,)",
        "semicolon": "Puntkomma (;)",
        "tab": "Tab",
        "pipe": "Pipe (|)",
        "success": "✅ Bestand succesvol geüpload! {count} records gevonden.",
        "preview": "👀 Voorbeeld van data",
        "col_mapping": "📋 Kolomtoewijzing",
        "col_mapping_text": "**Geef aan welke kolommen overeenkomen met de vereiste velden:**",
        "id_col": "ID Kolom",
        "sire_col": "Vader Kolom",
        "dam_col": "Moeder Kolom",
        "dob_col": "Geboortedatum Kolom",
        
        "check1_title": "1️⃣ Ontbrekende dieren",
        "check1_desc": "Zoek dieren die als ouder voorkomen maar niet zelf geregistreerd staan. Voeg deze dieren toe aan de stamboom (met onbekende ouders, onbekende geboortedatum, etc.)",
        "check1_btn": "Zoek ontbrekende dieren",
        "check1_metric": "Aantal ontbrekende dieren",
        "check1_download": "Download ontbrekende dieren",
        
        "check2_title": "2️⃣ Duplicaten",
        "check2_desc": "Zoek dieren die meerdere keren in het bestand staan. Check handmatig en verwijderen duplicaten zodat er maar 1 per dier overblijft.",
        "check2_btn": "Zoek duplicaten",
        "check2_metric": "Aantal duplicaten",
        "check2_download": "Download duplicaten",
        
        "check3_title": "3️⃣ Verdacht aantal nakomelingen",
        "check3_desc": "Top 20 vaders en moeders met de meeste nakomelingen. Dieren met onwaarschijnlijk veel nakomelingen (bijv vrouwelijke dieren met meer dan 30 nakomelingen) zijn 'verdacht'. In een dergelijk geval kunnen de nakomelingen beter een onbekende ouder krijgen (ofwel als een leeg veld of als een '0')",
        "check3_btn": "Tel nakomelingen",
        "check3_sires": "Top 20 Vaders",
        "check3_dams": "Top 20 Moeders",
        "check3_download_sires": "Download top vaders",
        "check3_download_dams": "Download top moeders",
        
        "check4_title": "4️⃣ Dieren met twee geslachten",
        "check4_desc": "Zoek dieren die als vader en als moeder in de stamboom staan. Check deze dieren handmatig en pas aan waar nodig (bijv. als een hengst een keer als moeder staat, verwijder dan zijn ID uit de moederkolom)",
        "check4_btn": "Zoek dieren die zowel vader en moeder zijn",
        "check4_metric": "Aantal dieren die vader en moeder zijn",
        "check4_success": "ZIP bestand aangemaakt met {count} individuele CSV-bestanden en een overzichtsbestand",
        "check4_download": "Download ZIP Bestand",
        "check4_overview": "Overzicht dubbele rollen",
        
        "check5_title": "5️⃣ Geboortedatum inconsistenties",
        "check5_desc": "Zoek dieren die geboren zijn voor hun ouders. Let wel: vaak zijn dit dieren (nakomelingen en/of ouders) waarvan de geboortedatum eigenlijk onbekend was, en die bijv. op 1-1-1900 zijn gezet. Voor andere inconsitenties, kan het zijn dat de afstamming niet klopt, of dat de geboortedatum van de nakomeling of het ouderdier niet klopt. Verwijder in al deze gevallen de geboortedata van de berekening van het generatieinterval.",
        "check5_btn": "Controleer geboortedata",
        "check5_metric": "Aantal datum inconsistenties",
        "check5_download": "Download inconsistente records",
        
        "check6_title": "6️⃣ Kringverwijzingen",
        "check6_desc": "Detecteer kringverwijzingen in de stamboomstructuur. Bij kringverwijzingen is een dier een voorouder van zichzelf (bijv. de ouder van zichzelf). Check deze kringverwijzingen handmatig en pas aan in de afstamming.",
        "check6_btn": "Zoek kringverwijzingen",
        "check6_found": "⚠️ {count} kringverwijzing(en) gevonden!",
        "check6_number": "Kringverwijzing {num}",
        "check6_path": "**Pad:**",
        "check6_download": "Download kringverwijzingen rapport",
        "check6_none": "Geen kringverwijzingen gevonden! ✅",
        
        "empty_state": "👆 Upload een stamboom CSV-bestand om te starten",
        "format_title": "📄 Verwacht Bestandsformaat",
        "format_desc": "Uw bestand moet er ongeveer zo uitzien (mag meer kolommen bevatten, en andere kolomnamen hebben):",
        "tip": "💡 **Tip:** Ouder-ID's met waarde `0` worden behandeld als onbekend.",
        "error": "Fout bij het lezen van bestand: {error}",
        
        "offspring_count": "Aantal_Nakomelingen",
        "as_sire": "Als_Vader",
        "as_dam": "Als_Moeder",
    },
    "EN": {
        "title": "🐴 Pedigree cleaning: check common issues",
        "subtitle": "Upload your pedigree file and perform various quality checks.",
        "upload": "Upload Pedigree File (CSV)",
        "separator": "File Separator",
        "comma": "Comma (,)",
        "semicolon": "Semicolon (;)",
        "tab": "Tab",
        "pipe": "Pipe (|)",
        "success": "✅ File uploaded successfully! {count} records found.",
        "preview": "👀 Data Preview",
        "col_mapping": "📋 Column Mapping",
        "col_mapping_text": "**Specify which columns correspond to the required fields:**",
        "id_col": "ID Column",
        "sire_col": "Sire Column",
        "dam_col": "Dam Column",
        "dob_col": "Date of Birth Column",
        
        "check1_title": "1️⃣ Missing Animals",
        "check1_desc": "Find animals that appear as parents but are not registered themselves. Add these animals to the pedigree (with unknown parents, unknown date of birth, etc.)",
        "check1_btn": "Find Missing Animals",
        "check1_metric": "Number of Missing Animals",
        "check1_download": "Download Missing Animals",
        
        "check2_title": "2️⃣ Duplicates",
        "check2_desc": "Find animals that appear multiple times in the file. Check manually and remove duplicates so only 1 remains per animal.",
        "check2_btn": "Find Duplicates",
        "check2_metric": "Number of Duplicates",
        "check2_download": "Download Duplicates",
        
        "check3_title": "3️⃣ Suspicious Number of Offspring",
        "check3_desc": "Top 20 sires and dams with the most offspring. Animals with an unlikely number of offspring (e.g., female animals with more than 30 offspring) are 'suspicious'. In such cases, the offspring should better have an unknown parent (either as an empty field or as a '0')",
        "check3_btn": "Count Offspring",
        "check3_sires": "Top 20 Sires",
        "check3_dams": "Top 20 Dams",
        "check3_download_sires": "Download Top Sires",
        "check3_download_dams": "Download Top Dams",
        
        "check4_title": "4️⃣ Animals with Two Genders",
        "check4_desc": "Find animals that appear as both sire and dam in the pedigree. Check these animals manually and adjust where necessary (e.g., if a stallion appears once as a dam, remove its ID from the dam column)",
        "check4_btn": "Find Animals That Are Both Sire and Dam",
        "check4_metric": "Number of Animals That Are Both Sire and Dam",
        "check4_success": "ZIP file created with {count} individual CSV files and an overview file",
        "check4_download": "Download ZIP File",
        "check4_overview": "Dual Role Overview",
        
        "check5_title": "5️⃣ Birth Date Inconsistencies",
        "check5_desc": "Find animals born before their parents. Note: often these are animals (offspring and/or parents) whose date of birth was actually unknown and was set to e.g. 1-1-1900. For other inconsistencies, it may be that the pedigree is incorrect, or that the date of birth of the offspring or parent animal is incorrect. In all these cases, remove the birth dates from the generation interval calculation.",
        "check5_btn": "Check Birth Dates",
        "check5_metric": "Number of Date Inconsistencies",
        "check5_download": "Download Inconsistent Records",
        
        "check6_title": "6️⃣ Circular References",
        "check6_desc": "Detect circular references in the pedigree structure. With circular references, an animal is an ancestor of itself (e.g., its own parent). Check these circular references manually and adjust the pedigree.",
        "check6_btn": "Find Circular References",
        "check6_found": "⚠️ {count} circular reference(s) found!",
        "check6_number": "Circular Reference {num}",
        "check6_path": "**Path:**",
        "check6_download": "Download Circular References Report",
        "check6_none": "No circular references found! ✅",
        
        "empty_state": "👆 Upload a pedigree CSV file to get started",
        "format_title": "📄 Expected File Format",
        "format_desc": "Your file should look something like this (may contain more columns and have different column names):",
        "tip": "💡 **Tip:** Parent IDs with value `0` are treated as unknown.",
        "error": "Error reading file: {error}",
        
        "offspring_count": "Offspring_Count",
        "as_sire": "As_Sire",
        "as_dam": "As_Dam",
    }
}

t = TRANSLATIONS[language]

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

# --------------------------------------------------
# Title
# --------------------------------------------------
h1(t["title"])
st.markdown(t["subtitle"])

# --------------------------------------------------
# Upload + separator
# --------------------------------------------------
col1, col2 = st.columns([3, 1])

with col1:
    uploaded_file = st.file_uploader(t["upload"], type=["csv"])

with col2:
    separator = st.selectbox(
        t["separator"],
        options=[",", ";", "\t", "|"],
        format_func=lambda x: {
            ",": t["comma"],
            ";": t["semicolon"],
            "\t": t["tab"],
            "|": t["pipe"]
        }[x],
    )

# --------------------------------------------------
# Main logic
# --------------------------------------------------
if uploaded_file is not None:
    try:
        # Try reading with UTF-8 encoding first, fallback to latin1
        try:
            df = pd.read_csv(uploaded_file, sep=separator, encoding='utf-8')
        except UnicodeDecodeError:
            uploaded_file.seek(0)  # Reset file pointer
            df = pd.read_csv(uploaded_file, sep=separator, encoding='latin1')
        
        st.success(t["success"].format(count=len(df)))

        with st.expander(t["preview"]):
            st.dataframe(df.head(10), use_container_width=True)

        # --------------------------------------------------
        # Column mapping
        # --------------------------------------------------
        h2(t["col_mapping"])
        st.markdown(t["col_mapping_text"])

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            id_col = st.selectbox(t["id_col"], df.columns)
        with c2:
            sire_col = st.selectbox(t["sire_col"], df.columns, index=min(1, len(df.columns)-1))
        with c3:
            dam_col = st.selectbox(t["dam_col"], df.columns, index=min(2, len(df.columns)-1))
        with c4:
            dob_col = st.selectbox(t["dob_col"], df.columns, index=min(3, len(df.columns)-1))

        df[id_col] = df[id_col].astype(str)
        df[sire_col] = df[sire_col].astype(str)
        df[dam_col] = df[dam_col].astype(str)
        df[dob_col] = pd.to_datetime(df[dob_col], errors="coerce")

        st.divider()

        # --------------------------------------------------
        # Check 1
        # --------------------------------------------------
        h2(t["check1_title"])
        st.markdown(t["check1_desc"])

        if st.button(t["check1_btn"]):
            all_ids = set(df[id_col])
            parents = (set(df[sire_col]) | set(df[dam_col])) - {"0", "", "nan", "None"}
            missing = parents - all_ids

            st.metric(t["check1_metric"], len(missing))

            if missing:
                missing_df = pd.DataFrame({id_col: sorted(missing)})
                st.dataframe(missing_df, hide_index=True, use_container_width=True)
                st.download_button(
                    t["check1_download"],
                    missing_df.to_csv(index=False),
                    "ontbrekende_dieren.csv" if language == "NL" else "missing_animals.csv",
                )

        st.divider()

        # --------------------------------------------------
        # Check 2
        # --------------------------------------------------
        h2(t["check2_title"])
        st.markdown(t["check2_desc"])

        if st.button(t["check2_btn"]):
            dupes = df[df.duplicated(id_col, keep=False)]
            st.metric(t["check2_metric"], dupes[id_col].nunique())

            if not dupes.empty:
                st.dataframe(dupes.sort_values(id_col), hide_index=True, use_container_width=True)
                st.download_button(
                    t["check2_download"],
                    dupes.to_csv(index=False),
                    "duplicaten.csv" if language == "NL" else "duplicates.csv",
                )

        st.divider()

        # --------------------------------------------------
        # Check 3
        # --------------------------------------------------
        h2(t["check3_title"])
        st.markdown(t["check3_desc"])

        if st.button(t["check3_btn"], key="check3"):
            # Count offspring for sires
            sire_counts = df[df[sire_col].isin(set(df[sire_col]) - {'0', '', 'nan'})].groupby(sire_col).size()
            sire_counts = sire_counts.sort_values(ascending=False).head(20)
            
            # Count offspring for dams
            dam_counts = df[df[dam_col].isin(set(df[dam_col]) - {'0', '', 'nan'})].groupby(dam_col).size()
            dam_counts = dam_counts.sort_values(ascending=False).head(20)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(t["check3_sires"])
                # Create dataframe with offspring count and full records
                sire_ids = sire_counts.index.tolist()
                sire_records = df[df[id_col].isin(sire_ids)].copy()
                
                # Add offspring count column
                sire_records[t["offspring_count"]] = sire_records[id_col].map(sire_counts)
                
                # Reorder columns: Aantal_Nakomelingen first, then all original columns
                cols = [t["offspring_count"]] + [col for col in sire_records.columns if col != t["offspring_count"]]
                sire_df = sire_records[cols].sort_values(t["offspring_count"], ascending=False).reset_index(drop=True)
                
                st.dataframe(sire_df, use_container_width=True, hide_index=True)
                
                csv_sires = sire_df.to_csv(index=False)
                st.download_button(
                    label=t["check3_download_sires"],
                    data=csv_sires,
                    file_name="top_vaders.csv" if language == "NL" else "top_sires.csv",
                    mime="text/csv",
                    key="download3a"
                )
            
            with col2:
                st.subheader(t["check3_dams"])
                # Create dataframe with offspring count and full records
                dam_ids = dam_counts.index.tolist()
                dam_records = df[df[id_col].isin(dam_ids)].copy()
                
                # Add offspring count column
                dam_records[t["offspring_count"]] = dam_records[id_col].map(dam_counts)
                
                # Reorder columns: Aantal_Nakomelingen first, then all original columns
                cols = [t["offspring_count"]] + [col for col in dam_records.columns if col != t["offspring_count"]]
                dam_df = dam_records[cols].sort_values(t["offspring_count"], ascending=False).reset_index(drop=True)
                
                st.dataframe(dam_df, use_container_width=True, hide_index=True)
                
                csv_dams = dam_df.to_csv(index=False)
                st.download_button(
                    label=t["check3_download_dams"],
                    data=csv_dams,
                    file_name="top_moeders.csv" if language == "NL" else "top_dams.csv",
                    mime="text/csv",
                    key="download3b"
                )
        
        st.divider()

        # --------------------------------------------------
        # Check 4 - Updated to create individual CSV files
        # --------------------------------------------------
        h2(t["check4_title"])
        st.markdown(t["check4_desc"])
        
        if st.button(t["check4_btn"], key="check4"):
            # Get animals that appear as both sire and dam
            sires = set(df[sire_col].unique()) - {'0', '', 'nan', 'None'}
            dams = set(df[dam_col].unique()) - {'0', '', 'nan', 'None'}
            both_roles = sires & dams
            
            st.metric(t["check4_metric"], len(both_roles))
            
            if len(both_roles) > 0:
                # Create ZIP file with individual CSV files
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    # Create overview dataframe
                    overview_data = []
                    
                    for animal_id in sorted(both_roles):
                        # Get records where this animal is sire or dam
                        records = df[(df[sire_col] == animal_id) | (df[dam_col] == animal_id)]
                        
                        # Count appearances as sire and dam
                        as_sire = (df[sire_col] == animal_id).sum()
                        as_dam = (df[dam_col] == animal_id).sum()
                        
                        overview_data.append({
                            id_col: animal_id,
                            t["as_sire"]: as_sire,
                            t["as_dam"]: as_dam
                        })
                        
                        # Create individual CSV for this animal
                        csv_content = records.to_csv(index=False)
                        filename = f"animal_{animal_id}.csv"
                        zip_file.writestr(filename, csv_content)
                    
                    # Create overview CSV
                    overview_df = pd.DataFrame(overview_data)
                    overview_csv = overview_df.to_csv(index=False)
                    overview_filename = "overzicht_dubbele_rollen.csv" if language == "NL" else "dual_role_overview.csv"
                    zip_file.writestr(overview_filename, overview_csv)
                
                zip_buffer.seek(0)
                
                st.success(t["check4_success"].format(count=len(both_roles)))
                
                # Show overview in the app
                st.subheader(t["check4_overview"])
                st.dataframe(overview_df, hide_index=True, use_container_width=True)
                
                st.download_button(
                    label=t["check4_download"],
                    data=zip_buffer,
                    file_name="dubbele_rol_dieren.zip" if language == "NL" else "dual_role_animals.zip",
                    mime="application/zip",
                    key="download4"
                )
        
        st.divider()

        # --------------------------------------------------
        # Check 5
        # --------------------------------------------------
        h2(t["check5_title"])
        st.markdown(t["check5_desc"])
        
        if st.button(t["check5_btn"], key="check5"):
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
                            problems.append('vader' if language == "NL" else 'sire')
                    
                    # Check dam
                    if dam_id in date_lookup and dam_id not in ['0', '', 'nan']:
                        dam_dob = date_lookup[dam_id]
                        if pd.notna(dam_dob) and animal_dob <= dam_dob:
                            problems.append('moeder' if language == "NL" else 'dam')
                    
                    if problems:
                        if language == "NL":
                            col_names = {
                                'animal_id': 'Dier_ID',
                                'animal_dob': 'Geboortedatum_Dier',
                                'sire_id': 'Vader_ID',
                                'sire_dob': 'Geboortedatum_Vader',
                                'dam_id': 'Moeder_ID',
                                'dam_dob': 'Geboortedatum_Moeder',
                                'problem': 'Probleem_bij'
                            }
                        else:
                            col_names = {
                                'animal_id': 'Animal_ID',
                                'animal_dob': 'Animal_DOB',
                                'sire_id': 'Sire_ID',
                                'sire_dob': 'Sire_DOB',
                                'dam_id': 'Dam_ID',
                                'dam_dob': 'Dam_DOB',
                                'problem': 'Problem_In'
                            }
                        
                        inconsistency_data.append({
                            col_names['animal_id']: animal_id,
                            col_names['animal_dob']: animal_dob.strftime('%d-%m-%Y') if pd.notna(animal_dob) else '',
                            col_names['sire_id']: sire_id if sire_id not in ['0', '', 'nan'] else '',
                            col_names['sire_dob']: sire_dob.strftime('%d-%m-%Y') if pd.notna(sire_dob) else '',
                            col_names['dam_id']: dam_id if dam_id not in ['0', '', 'nan'] else '',
                            col_names['dam_dob']: dam_dob.strftime('%d-%m-%Y') if pd.notna(dam_dob) else '',
                            col_names['problem']: ', '.join(problems)
                        })
            
            st.metric(t["check5_metric"], len(inconsistency_data))
            
            if len(inconsistency_data) > 0:
                inconsistent_df = pd.DataFrame(inconsistency_data)
                st.dataframe(inconsistent_df, hide_index=True, use_container_width=True)
                
                csv = inconsistent_df.to_csv(index=False)
                st.download_button(
                    label=t["check5_download"],
                    data=csv,
                    file_name="geboortedatum_inconsistenties.csv" if language == "NL" else "birth_date_inconsistencies.csv",
                    mime="text/csv",
                    key="download5"
                )
        
        st.divider()

        # --------------------------------------------------
        # Check 6
        # --------------------------------------------------
        h2(t["check6_title"])
        st.markdown(t["check6_desc"])
        
        if st.button(t["check6_btn"], key="check6"):
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
                st.error(t["check6_found"].format(count=len(circular_refs)))
                st.markdown("---")
                
                for i, cycle in enumerate(circular_refs, 1):
                    st.markdown(f"### {t['check6_number'].format(num=i)}")
                    st.markdown(f"{t['check6_path']} `{' → '.join(cycle)}`")
                    st.markdown("---")
                
                # Create downloadable report
                report_lines = []
                for i, cycle in enumerate(circular_refs, 1):
                    label = t["check6_number"].format(num=i)
                    report_lines.append(f"{label}: {' → '.join(cycle)}")
                
                report_text = '\n'.join(report_lines)
                st.download_button(
                    label=t["check6_download"],
                    data=report_text,
                    file_name="kringverwijzingen.txt" if language == "NL" else "circular_references.txt",
                    mime="text/plain",
                    key="download6"
                )
            else:
                st.success(t["check6_none"])

    except Exception as e:
        st.error(t["error"].format(error=str(e)))

# --------------------------------------------------
# Empty state
# --------------------------------------------------
else:
    st.info(t["empty_state"])

    h2(t["format_title"])
    st.markdown(t["format_desc"])
    st.code(
        """ID,Vader,Moeder,Geboortedatum
141209548,0,0,1-1-1970
141209555,0,0,1-1-1967
15,141209548,141209555,1-1-1941""" if language == "NL" else 
        """ID,Sire,Dam,DateOfBirth
141209548,0,0,1-1-1970
141209555,0,0,1-1-1967
15,141209548,141209555,1-1-1941"""
    )

st.divider()
st.markdown(t["tip"])
