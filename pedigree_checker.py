import streamlit as st
import pandas as pd
import io
from datetime import datetime
from collections import defaultdict

st.set_page_config(page_title="Stamboom Controle", layout="wide")

# Custom CSS to increase font sizes
st.markdown("""
    <style>
    /* Increase base font size for main content */
    html, body, [class*="css"] {
        font-size: 20px;
    }
    
    /* Main body text and paragraphs */
    p, div, span, label {
        font-size: 20px !important;
    }
    
    /* MAIN TITLE - Very specific selector for Streamlit Cloud */
    .main h1, 
    div[data-testid="stMarkdownContainer"] h1,
    .element-container h1 {
        font-size: 3rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
        line-height: 1.2 !important;
        color: #262730 !important;
    }
    
    /* Additional title targeting */
    h1 {
        font-size: 3rem !important;
        font-weight: 700 !important;
    }
    
    /* SECTION HEADERS - More specific selectors */
    .main h2,
    div[data-testid="stMarkdownContainer"] h2,
    .element-container h2 {
        font-size: 2rem !important;
        font-weight: 600 !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
        color: #262730 !important;
    }
    
    h2 {
        font-size: 2rem !important;
        font-weight: 600 !important;
    }
    
    /* SUBHEADERS */
    .main h3,
    div[data-testid="stMarkdownContainer"] h3,
    .element-container h3 {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
    }
    
    h3 {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
    }
    
    /* Increase button text */
    .stButton button {
        font-size: 20px !important;
        padding: 0.85rem 1.75rem !important;
        font-weight: 500 !important;
    }
    
    /* Increase selectbox and input text */
    .stSelectbox label, .stTextInput label {
        font-size: 20px !important;
        font-weight: 600 !important;
    }
    
    .stSelectbox div[data-baseweb="select"] > div {
        font-size: 20px !important;
    }
    
    /* Increase metric text */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1.5rem !important;
        font-weight: 500 !important;
    }
    
    /* Increase dataframe text significantly */
    .dataframe {
        font-size: 18px !important;
    }
    
    .dataframe th {
        font-size: 20px !important;
        font-weight: 600 !important;
        padding: 12px !important;
    }
    
    .dataframe td {
        font-size: 18px !important;
        padding: 10px !important;
    }
    
    /* Increase markdown text */
    .stMarkdown {
        font-size: 20px !important;
    }
    
    .stMarkdown p {
        font-size: 20px !important;
    }
    
    /* Increase file uploader text */
    .stFileUploader label {
        font-size: 20px !important;
        font-weight: 600 !important;
    }
    
    .stFileUploader div {
        font-size: 20px !important;
    }
    
    /* Increase expander text */
    .streamlit-expanderHeader {
        font-size: 20px !important;
        font-weight: 500 !important;
    }
    
    /* Increase download button text */
    .stDownloadButton button {
        font-size: 20px !important;
        padding: 0.85rem 1.75rem !important;
        font-weight: 500 !important;
    }
    
    /* Success, error, warning, info messages */
    .stAlert {
        font-size: 22px !important;
    }
    
    .stAlert > div {
        font-size: 20px !important;
    }
    
    /* Code blocks */
    code {
        font-size: 16px !important;
        line-height: 1.6 !important;
    }
    
    /* Column labels in selectbox */
    [role="option"] {
        font-size: 20px !important;
        padding: 10px !important;
    }
    
    /* Divider with more spacing */
    hr {
        margin: 3rem 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Use HTML for title with inline styling to ensure it works on Streamlit Cloud
st.markdown("""
    <h1 style='font-size: 48px; font-weight: 700; margin-bottom: 20px; color: #262730;'>
        🐴 Stamboom voorbereiding - controleer op veelvoorkomende fouten
    </h1>
    """, unsafe_allow_html=True)

st.markdown("Upload uw stamboombestand en voer verschillende kwaliteitscontroles uit.")

# File upload and separator selection
col1, col2 = st.columns([3, 1])

with col1:
    uploaded_file = st.file_uploader("Upload Stamboombestand (CSV)", type=['csv'])

with col2:
    separator = st.selectbox(
        "Bestandsscheidingsteken",
        options=[",", ";", "\t", "|"],
        format_func=lambda x: {"," : "Komma (,)", ";" : "Puntkomma (;)", "\t" : "Tab", "|" : "Pipe (|)"}[x],
        index=0
    )

if uploaded_file is not None:
    # Read the file
    try:
        df = pd.read_csv(uploaded_file, sep=separator)
        st.success(f"✅ Bestand succesvol geüpload! {len(df)} records gevonden.")
        
        # Show preview
        with st.expander("👀 Voorbeeld van data"):
            st.dataframe(df.head(10), use_container_width=True)
        
        # Column mapping section
        st.markdown("<h2 style='font-size: 32px; font-weight: 600; margin-top: 30px; margin-bottom: 15px;'>📋 Kolomtoewijzing</h2>", unsafe_allow_html=True)
        st.markdown("**Geef aan welke kolommen overeenkomen met de vereiste velden:**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            id_col = st.selectbox("ID Kolom", options=df.columns.tolist(), index=0)
        with col2:
            sire_col = st.selectbox("Vader Kolom", options=df.columns.tolist(), 
                                   index=1 if len(df.columns) > 1 else 0)
        with col3:
            dam_col = st.selectbox("Moeder Kolom", options=df.columns.tolist(), 
                                  index=2 if len(df.columns) > 2 else 0)
        with col4:
            dob_col = st.selectbox("Geboortedatum Kolom", options=df.columns.tolist(), 
                                  index=3 if len(df.columns) > 3 else 0)
        
        # Convert columns to appropriate types
        df[id_col] = df[id_col].astype(str)
        df[sire_col] = df[sire_col].astype(str)
        df[dam_col] = df[dam_col].astype(str)
        
        # Parse dates
        try:
            df[dob_col] = pd.to_datetime(df[dob_col], format='%d-%m-%Y', errors='coerce')
        except:
            try:
                df[dob_col] = pd.to_datetime(df[dob_col], errors='coerce')
            except:
                st.warning("Kon niet alle datums parsen. Sommige datumcontroles werken mogelijk niet.")
        
        st.divider()
        
        # Check 1: Missing Parents
        st.markdown("<h2 style='font-size: 32px; font-weight: 600; margin-top: 30px; margin-bottom: 15px;'>1️⃣ Ontbrekende dieren</h2>", unsafe_allow_html=True)
        st.markdown("Zoek dieren die als ouder voorkomen maar niet zelf geregistreerd staan.")
        
        if st.button("Zoek ontbrekende dieren", key="check1"):
            # Get all IDs in the pedigree
            all_ids = set(df[id_col].unique())
            
            # Get all parents (excluding '0' and empty values)
            all_sires = set(df[sire_col].unique()) - {'0', '', 'nan', 'None'}
            all_dams = set(df[dam_col].unique()) - {'0', '', 'nan', 'None'}
            all_parents = all_sires | all_dams
            
            # Find missing parents
            missing_parents = all_parents - all_ids
            
            st.metric("Aantal ontbrekende dieren:", len(missing_parents))
            
            if len(missing_parents) > 0:
                # Create a dataframe with missing parents
                missing_df = pd.DataFrame({
                    id_col: sorted(list(missing_parents)),
                })
                # Add other columns with empty/missing values
                for col in df.columns:
                    if col not in [id_col]:
                        missing_df[col] = ''
                
                st.dataframe(missing_df, use_container_width=True)
                
                # Download button
                csv = missing_df.to_csv(index=False)
                st.download_button(
                    label="Download ontbrekende dieren",
                    data=csv,
                    file_name="ontbrekende_dieren.csv",
                    mime="text/csv",
                    key="download1"
                )
        
        st.divider()
        
        # Check 2: Duplicate IDs
        st.markdown("<h2 style='font-size: 32px; font-weight: 600; margin-top: 30px; margin-bottom: 15px;'>2️⃣ Duplicaten</h2>", unsafe_allow_html=True)
        st.markdown("Zoek dieren die meerdere keren in het bestand staan op basis van de ID kolom.")
        
        if st.button("Zoek duplicaten", key="check2"):
            # Find duplicates - keep=False ensures ALL occurrences of duplicates are included
            duplicates = df[df.duplicated(subset=[id_col], keep=False)]
            duplicate_ids = duplicates[id_col].unique()
            
            st.metric("Aantal duplicaten", len(duplicate_ids))
            
            if len(duplicate_ids) > 0:
                st.dataframe(duplicates.sort_values(by=id_col), use_container_width=True)
                
                # Download button
                csv = duplicates.to_csv(index=False)
                st.download_button(
                    label="Download duplicaten",
                    data=csv,
                    file_name="duplicaten.csv",
                    mime="text/csv",
                    key="download2"
                )
        
        st.divider()
        
        # Check 3: Offspring Count
        st.markdown("<h2 style='font-size: 32px; font-weight: 600; margin-top: 30px; margin-bottom: 15px;'>3️⃣ Verdacht aantal nakomelingen</h2>", unsafe_allow_html=True)
        st.markdown("Identificeer top 20 vaders en moeders met de meeste nakomelingen. Dieren met onwaarschijnlijk veel nakomelingen (bijv vrouwelijke dieren met meer dan 30 nakomelingen) zijn 'verdacht'.")
        
        if st.button("Tel nakomelingen", key="check3"):
            # Count offspring for sires
            sire_counts = df[df[sire_col].isin(set(df[sire_col]) - {'0', '', 'nan'})].groupby(sire_col).size()
            sire_counts = sire_counts.sort_values(ascending=False).head(20)
            
            # Count offspring for dams
            dam_counts = df[df[dam_col].isin(set(df[dam_col]) - {'0', '', 'nan'})].groupby(dam_col).size()
            dam_counts = dam_counts.sort_values(ascending=False).head(20)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Top 20 Vaders")
                sire_df = pd.DataFrame({
                    'ID': sire_counts.index,
                    'Aantal Nakomelingen': sire_counts.values
                }).reset_index(drop=True)
                st.dataframe(sire_df, use_container_width=True, hide_index=True)
                
                csv_sires = sire_df.to_csv(index=False)
                st.download_button(
                    label="Download top vaders",
                    data=csv_sires,
                    file_name="top_vaders.csv",
                    mime="text/csv",
                    key="download3a"
                )
            
            with col2:
                st.subheader("Top 20 Moeders")
                dam_df = pd.DataFrame({
                    'ID': dam_counts.index,
                    'Aantal Nakomelingen': dam_counts.values
                }).reset_index(drop=True)
                st.dataframe(dam_df, use_container_width=True, hide_index=True)
                
                csv_dams = dam_df.to_csv(index=False)
                st.download_button(
                    label="Download top moeders",
                    data=csv_dams,
                    file_name="top_moeders.csv",
                    mime="text/csv",
                    key="download3b"
                )
        
        st.divider()
        
        # Check 4: Animals as both Sire and Dam
        st.markdown("<h2 style='font-size: 32px; font-weight: 600; margin-top: 30px; margin-bottom: 15px;'>4️⃣ Dieren met twee geslachten</h2>", unsafe_allow_html=True)
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
        
        # Check 5: Birth Date Inconsistencies
        st.markdown("<h2 style='font-size: 32px; font-weight: 600; margin-top: 30px; margin-bottom: 15px;'>5️⃣ Geboortedatum inconsistenties</h2>", unsafe_allow_html=True)
        st.markdown("Zoek dieren die geboren zijn voor hun ouders. Let wel: vaak zijn dit dieren waarvan de geboortedatum eigenlijk onbekend was, en die bijv. op 1-1-1900 zijn gezet. Let op dat deze niet worden meegnoemen in het berekenen van het generatieinterval. Voor andere inconsitenties, kan het zijn dat de afstamming niet klopt, of dat de geboortedatum van de nakomeling of het ouderdier niet klopt.")
        
        if st.button("Voer geboortedatum controle uit", key="check5"):
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
                            'Geboortedatum_Dier': animal_dob,
                            'Vader_ID': sire_id if sire_id not in ['0', '', 'nan'] else '',
                            'Geboortedatum_Vader': sire_dob if pd.notna(sire_dob) else '',
                            'Moeder_ID': dam_id if dam_id not in ['0', '', 'nan'] else '',
                            'Geboortedatum_Moeder': dam_dob if pd.notna(dam_dob) else '',
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
        
        # Check 6: Circular References (Kringverwijzingen)
        st.markdown("<h2 style='font-size: 32px; font-weight: 600; margin-top: 30px; margin-bottom: 15px;'>6️⃣ Kringverwijzingen</h2>", unsafe_allow_html=True)
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
        st.error(f"Fout bij het lezen van bestand: {str(e)}")
        st.info("Zorg ervoor dat uw bestand een geldig CSV-bestand is.")

else:
    st.info("👆 **Upload een stamboom CSV-bestand om de analyse te starten**")
    st.markdown("")
    
    # Show example format
    st.subheader("📄 Verwacht Bestandsformaat")
    st.markdown("Uw bestand moet er ongeveer zo uitzien (mag meer kolommen bevatten, en andere kolomnamen hebben):")
    st.code("""ID,Vader,Moeder,Geboortedatum
141209548,0,0,1-1-1970
141209555,0,0,1-1-1967
15,141209548,141209555,1-1-1941
47,0,0,1-1-1949""")
    st.markdown("**Let op:** U kunt ook puntkomma's (;) of andere scheidingstekens gebruiken - selecteer gewoon de juiste optie hierboven!")

# Footer
st.divider()
st.markdown("**💡 Tip:** Ouder-ID's gemarkeerd als '0' worden behandeld als onbekende/ontbrekende ouders.")