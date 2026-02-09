# Stamboom Controle Tool

Een uitgebreide tool voor het analyseren en valideren van stamboomgegevens met meerdere kwaliteitscontroles.

## Functionaliteiten

1. **Ontbrekende Dieren**: Identificeert dieren die als ouder voorkomen maar niet zelf in de stamboomlijst staan
2. **Duplicaten**: Vindt dubbele entries in de ID kolom (dieren die 2 of meer keer voorkomen)
3. **Verdacht Aantal Nakomelingen**: Toont top 20 vaders en moeders op basis van aantal nakomelingen
4. **Dieren met Twee Geslachten**: Identificeert dieren die zowel als vader en als moeder voorkomen
5. **Geboortedatum Inconsistenties**: Vindt dieren die geboren zijn voor hun ouders
6. **Kringverwijzingen**: Detecteert circulaire referenties in de stamboomstructuur

## Gebruik

1. Upload uw stamboom CSV-bestand
2. Selecteer het juiste scheidingsteken (komma, puntkomma, tab, of pipe)
3. Wijs de kolommen toe aan de vereiste velden:
   - ID (dieridentificatie)
   - Vader (vader ID)
   - Moeder (moeder ID)
   - Geboortedatum
4. Voer individuele controles uit door op de corresponderende knoppen te klikken
5. Download de resultaten voor elke controle indien nodig

## Bestandsformaat

Uw CSV-bestand moet minimaal de volgende kolommen bevatten:
- Dier ID
- Vader ID (gebruik '0' voor onbekend)
- Moeder ID (gebruik '0' voor onbekend)
- Geboortedatum (bij voorkeur in formaat: d-m-jjjj)

Voorbeeld:
```
ID,Vader,Moeder,Geboortedatum
141209548,0,0,1-1-1970
141209555,0,0,1-1-1967
15,141209548,141209555,1-1-1985
47,0,0,1-1-1949
```

Het bestand mag meer kolommen bevatten en andere kolomnamen hebben - u kunt deze in de app toewijzen.

## Output Bestanden

- **Ontbrekende Dieren**: CSV-bestand met records die aan de stamboom toegevoegd moeten worden
- **Duplicaten**: CSV-bestand met alle dubbele records
- **Top Vaders/Moeders**: Twee CSV-bestanden met top 20 dieren op basis van aantal nakomelingen
- **Dubbele-Rol Dieren**: Excel-bestand met aparte tabbladen voor elk dier
- **Geboortedatum Inconsistenties**: CSV-bestand met gedetailleerde informatie over problematische records
- **Kringverwijzingen**: Tekstbestand met alle circulaire referentie ketens
