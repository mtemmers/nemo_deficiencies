-- ================================================================================
-- NEMO DQM Report SQL
-- Report: (DEFICIENCIES) Teile
-- Internal Name: deficiencies_parts
-- Generiert am: 2026-07-29T13:52:03+02:00
-- Generator: nemo_deficiencies SQL generator
-- Prüfblöcke: 17
-- Regeln aktiv/inaktiv: 62 / 9
-- DQ-Typen: Vollständigkeit=15, Validität=16, Korrektheit=5, Konsistenz=2, Aktualität=2, Genauigkeit=5, Redundanz=4, Einheitlichkeit=15, Relevanz=6, Verständlichkeit=1
-- --------------------------------------------------------------------------------
-- Checks:
--   01. PART_ARCHIVED (Archivierungsstatus) (2 aktiv / 0 inaktiv) - Validität, Vollständigkeit
--   02. PART_I_D (Teilenummer) (5 aktiv / 0 inaktiv) - Einheitlichkeit, Genauigkeit, Validität, Vollständigkeit
--   03. PART_DESC1-4 (Teilebezeichnungen) (7 aktiv / 0 inaktiv) - Einheitlichkeit, Genauigkeit, Redundanz, Relevanz, Validität, Verständlichkeit, Vollständigkeit
--   04. Prüfung 4 (4 aktiv / 1 inaktiv) - Einheitlichkeit, Genauigkeit, Redundanz, Relevanz, Validität
--   05. Prüfung 5 (4 aktiv / 1 inaktiv) - Einheitlichkeit, Genauigkeit, Redundanz, Relevanz, Validität
--   06. Prüfung 6 (4 aktiv / 1 inaktiv) - Einheitlichkeit, Genauigkeit, Redundanz, Relevanz, Validität
--   07. PART_SEARCH_TERM (Suchbegriff) (4 aktiv / 0 inaktiv) - Einheitlichkeit, Relevanz, Validität, Vollständigkeit
--   08. PART_SORT_DESC (Sortierbeschreibung) (4 aktiv / 0 inaktiv) - Einheitlichkeit, Relevanz, Validität, Vollständigkeit
--   09. PART_GROUP (Teilegruppe) (2 aktiv / 1 inaktiv) - Einheitlichkeit, Validität, Vollständigkeit
--   10. PART_TARIFF_NUMBER (Zolltarifnummer) (2 aktiv / 1 inaktiv) - Einheitlichkeit, Validität, Vollständigkeit
--   11. PART_STORAGE_UNIT (Lagermengeneinheit - LME) (2 aktiv / 1 inaktiv) - Einheitlichkeit, Validität, Vollständigkeit
--   12. PART_B_O_M_UNIT (Stücklistenmengeneinheit - BOM_ME) (2 aktiv / 1 inaktiv) - Einheitlichkeit, Validität, Vollständigkeit
--   13. STORAGE_WEIGHT und WEIGHT_UNIT (Gewichtsangaben) (5 aktiv / 2 inaktiv) - Einheitlichkeit, Konsistenz, Korrektheit, Validität, Vollständigkeit
--   14. PART_CREATION_DATE (Erstellungsdatum) (4 aktiv / 0 inaktiv) - Aktualität, Korrektheit, Vollständigkeit
--   15. PART_CREATION_USER (Erstellungsbenutzer) (3 aktiv / 0 inaktiv) - Einheitlichkeit, Validität, Vollständigkeit
--   16. PART_CHANGE_DATE (Änderungsdatum) (5 aktiv / 0 inaktiv) - Aktualität, Konsistenz, Korrektheit, Vollständigkeit
--   17. PART_CHANGE_USER (Änderungsbenutzer) (3 aktiv / 0 inaktiv) - Einheitlichkeit, Validität, Vollständigkeit
-- ================================================================================
WITH src AS (
    SELECT
        COMPANY,
        MASTER_DATA_SUB_TYPE,
        part_i_d,							-- #ERP-Origin: S_Artikel.Artikel
        part_group,							-- #ERP-Origin: S_Artikel.Artikelgruppe
        part_a_b_c_classification,			-- #ERP-Origin: S_Artikel.ABC_Klasse
        part_archived,						-- #ERP-Origin: S_Artikel.archiviert
        part_b_m_e_factor,					-- #ERP-Origin: S_Artikel.BME_Faktor
        part_b_o_m_factor,					-- #ERP-Origin: S_Artikel.StkFaktor
        part_b_o_m_formula,					-- #ERP-Origin: S_Artikel.StkFormel
        part_bom_line_type,					-- #ERP-Origin: S_Artikel.StkZeilenArt
        part_b_o_m_unit,					-- #ERP-Origin: S_Artikel.StkME
        part_business_unit,					-- #ERP-Origin: S_Artikel.Sparte
        part_business_unit_desc,			-- #ERP-Origin: S_Artikel.Bezeichnung
        part_change_date,					-- #ERP-Origin: S_Artikel.AenderungDatum
        part_change_user,					-- #ERP-Origin: S_Artikel.AenderungBenutzer
        part_creation_date,					-- #ERP-Origin: S_Artikel.AnlageDatum
        part_creation_user,					-- #ERP-Origin: S_Artikel.AnlageBenutzer
        part_c_r_o_warehouse,				-- #ERP-Origin: S_Artikel.KommLager
        part_desc1,							-- #ERP-Origin: S_ArtikelSpr.Bezeichnung[1]
        part_desc2,							-- #ERP-Origin: S_ArtikelSpr.Bezeichnung[2]
        part_desc3,							-- #ERP-Origin: S_ArtikelSpr.Bezeichnung[3]
        part_desc4,							-- #ERP-Origin: S_ArtikelSpr.Bezeichnung[4]
        part_min_replenishment_time,		-- #ERP-Origin: S_Artikel.WBZFaktor
        part_o_i_d,							-- #ERP-Origin: S_Artikel.S_Artikel_Obj
        part_origin_country,				-- #ERP-Origin: S_Artikel.Ursprungsland
        part_replenishment_time,			-- #ERP-Origin: S_Artikel.WBZ
        part_search_term,					-- #ERP-Origin: S_Artikel.Suchbegriff
        part_selection,						-- #ERP-Origin: S_Artikel.Selektion
        part_s_m_e_factor,					-- #ERP-Origin: S_Artikel.SME_Faktor
        part_sort_desc,						-- #ERP-Origin: S_Artikel.SortBezeichnung
        part_state,							-- #ERP-Origin: S_Artikel.Bundesland
        part_storage_unit,					-- #ERP-Origin: S_Artikel.LagerME
        part_storage_weight,				-- #ERP-Origin: S_Artikel.LagerGewicht
        part_supplier_replenishment,		-- #ERP-Origin: S_Artikel.WBZ_Lieferant
        part_tariff_number,					-- #ERP-Origin: S_Artikel.Zolltarifnummer
        part_time_unit_replenishment,		-- #ERP-Origin: S_Artikel.ZeiteinheitWBZ
        part_type,							-- #ERP-Origin: S_Artikel.ArtikelArt
        part_type_description,				-- #ERP-Origin: S_Artikel.Bezeichnung
        part_unit_replenishment,			-- #ERP-Origin: S_Artikel.ZeiteinheitWBZ
        part_variant_type,					-- #ERP-Origin: S_Artikel.ArtVarTyp
        part_variant_type_desc,				-- #ERP-Origin: S_ArtVarTypSpr.Bezeichnung
        part_weight,						-- #ERP-Origin: S_Artikel.Gewicht
        part_weight_confirmed,				-- #ERP-Origin: S_Artikel.GewichtBestaetigt
        part_weight_unit,					-- #ERP-Origin: S_Artikel.GewichtME
        part_work_group					    -- #ERP-Origin: S_Artikel.VerteilerGruppe
    FROM
        $schema.$table
    WHERE
        UPPER(TRIM(MASTER_DATA_SUB_TYPE)) = 'PART'
),

-- ----------------------------------------------------------------------------
-- CTE 2: proc_src - Verarbeitete Teile aus pa_export
-- ----------------------------------------------------------------------------
-- Filtert die Teile, die bereits im paDQM-System verarbeitet wurden
-- ----------------------------------------------------------------------------
proc_src AS (
    SELECT DISTINCT
        TRIM(CAST(COMPANY AS NVARCHAR(256))) AS COMPANY,
        TRIM(CAST(PART_I_D AS NVARCHAR(256))) AS PART_I_D
    FROM
        $schema."pa_export"
    WHERE
        PART_I_D IS NOT NULL
),

-- ----------------------------------------------------------------------------
-- CTE 3: joined - Verknüpfung von Stammdaten mit verarbeiteten Teilen
-- ----------------------------------------------------------------------------
-- Reduziert die Datenmenge auf nur die relevanten, bereits verarbeiteten Teile
-- ----------------------------------------------------------------------------
joined AS (
    SELECT
        c.*
    FROM
        src c
        INNER JOIN proc_src p 
            ON c.COMPANY = p.COMPANY
            AND c.PART_I_D = p.PART_I_D
),

-- ----------------------------------------------------------------------------
-- CTE 4: checks - Datenqualitätsprüfungen
-- ----------------------------------------------------------------------------
-- Führt umfassende Validierungen durch und erstellt eine Liste aller
-- gefundenen Mängel als konkatenierte Zeichenkette
-- ----------------------------------------------------------------------------
checks AS (
    SELECT
        s.*,
        (
            -- ================================================================
            -- PRÜFUNG 1: PartArchived
            -- Typen: Validität, Vollständigkeit
            CASE
                -- Vollständigkeit
                WHEN part_archived IS NULL OR TRIM(part_archived) = ''
                    THEN '|Archivierungsstatus leer'
                -- Validität
                WHEN UPPER(part_archived) NOT IN ('Y', 'N', 'TRUE', 'FALSE', '0', '1')
                    THEN '|Archivierungsstatus ungültig'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 2: PartID
            -- Vollständigkeit, Einzigartigkeit, Gültigkeit, Konsistenz
            -- Typen: Einheitlichkeit, Genauigkeit, Validität, Vollständigkeit
            CASE
                -- Vollständigkeit
                WHEN part_i_d IS NULL OR TRIM(part_i_d) = ''
                    THEN '|Teilenummer leer'
                -- Einheitlichkeit
                WHEN part_i_d <> TRIM(part_i_d)
                    THEN '|Teilenummer mit Leerzeichen'
                -- Validität
                WHEN part_i_d NOT LIKE_REGEXPR '.*[A-Z0-9].*' FLAG 'i'
                    THEN '|Teilenummer keine Buchstaben/Zahlen'
                -- Validität
                WHEN part_i_d NOT LIKE_REGEXPR '^[\p{L}\p{N}._/-]+$' FLAG 'i'
                    THEN '|Teilenummer ungültige Zeichen'
                -- Genauigkeit
                WHEN LENGTH(TRIM(part_i_d)) > 80
                    THEN '|Teilenummer zu lang'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 3: PartDesc1
            -- PART_DESC1 ist die primäre Pflichtbezeichnung; PART_DESC2-4 sind optional
            -- PART_DESC1
            -- Typen: Einheitlichkeit, Genauigkeit, Redundanz, Relevanz, Validität, Verständlichkeit, Vollständigkeit
            CASE
                -- Vollständigkeit
                WHEN PART_DESC1 IS NULL OR TRIM(PART_DESC1) = ''
                    THEN '|Teilebezeichnung 1 leer'
                -- Einheitlichkeit
                WHEN PART_DESC1 <> TRIM(PART_DESC1)
                    THEN '|Teilebezeichnung 1 mit Rand-Leerzeichen'
                -- Redundanz
                WHEN PART_DESC1 LIKE_REGEXPR '\s{2,}'
                    THEN '|Teilebezeichnung 1 mit mehrfachen Leerzeichen'
                -- Verständlichkeit
                WHEN PART_DESC1 NOT LIKE_REGEXPR '[\p{L}\p{N}]' FLAG 'i'
                    THEN '|Teilebezeichnung 1 ohne Buchstaben oder Zahlen'
                -- Validität
                WHEN PART_DESC1 LIKE_REGEXPR '[[:cntrl:]]'
                    THEN '|Teilebezeichnung 1 enthält Steuerzeichen'
                -- Genauigkeit
                WHEN LENGTH(TRIM(PART_DESC1)) > 255
                    THEN '|Teilebezeichnung 1 länger als 255 Zeichen'
                -- Relevanz
                WHEN PART_DESC1 LIKE_REGEXPR '([[:<:]]|^)(test|demo|dummy|muster|beispiel|nicht aktiv|inaktiv|gesperrt|obsolet|veraltet|ungültig|gelöscht|obsolete|deprecated|invalid|deleted|outdated|tbd|todo)([[:>:]]|$)' FLAG 'i'
                    THEN '|Teilebezeichnung 1 enthält Platzhalter oder obsolete Begriffe'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 4: PartDesc2
            -- PART_DESC2
            -- Typen: Einheitlichkeit, Genauigkeit, Redundanz, Relevanz, Validität
            CASE
                -- Einheitlichkeit
                WHEN COALESCE(PART_DESC2, '') <> '' AND PART_DESC2 <> TRIM(PART_DESC2)
                    THEN '' --'|Teilebezeichnung 2 mit Rand-Leerzeichen'
                -- Redundanz
                WHEN COALESCE(PART_DESC2, '') LIKE_REGEXPR '\s{2,}'
                    THEN '|Teilebezeichnung 2 mit mehrfachen Leerzeichen'
                -- Validität
                WHEN COALESCE(PART_DESC2, '') LIKE_REGEXPR '[[:cntrl:]]'
                    THEN '|Teilebezeichnung 2 enthält Steuerzeichen'
                -- Genauigkeit
                WHEN LENGTH(TRIM(COALESCE(PART_DESC2, ''))) > 255
                    THEN '|Teilebezeichnung 2 länger als 255 Zeichen'
                -- Relevanz
                WHEN COALESCE(PART_DESC2, '') LIKE_REGEXPR '([[:<:]]|^)(test|demo|dummy|muster|beispiel|nicht aktiv|inaktiv|gesperrt|obsolet|veraltet|ungültig|gelöscht|obsolete|deprecated|invalid|deleted|outdated|tbd|todo)([[:>:]]|$)' FLAG 'i'
                    THEN '|Teilebezeichnung 2 enthält Platzhalter oder obsolete Begriffe'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 5: PartDesc3
            -- PART_DESC3
            -- Typen: Einheitlichkeit, Genauigkeit, Redundanz, Relevanz, Validität
            CASE
                -- Einheitlichkeit
                WHEN COALESCE(PART_DESC3, '') <> '' AND PART_DESC3 <> TRIM(PART_DESC3)
                    THEN '' --'|Teilebezeichnung 3 mit Rand-Leerzeichen'
                -- Redundanz
                WHEN COALESCE(PART_DESC3, '') LIKE_REGEXPR '\s{2,}'
                    THEN '|Teilebezeichnung 3 mit mehrfachen Leerzeichen'
                -- Validität
                WHEN COALESCE(PART_DESC3, '') LIKE_REGEXPR '[[:cntrl:]]'
                    THEN '|Teilebezeichnung 3 enthält Steuerzeichen'
                -- Genauigkeit
                WHEN LENGTH(TRIM(COALESCE(PART_DESC3, ''))) > 255
                    THEN '|Teilebezeichnung 3 länger als 255 Zeichen'
                -- Relevanz
                WHEN COALESCE(PART_DESC3, '') LIKE_REGEXPR '([[:<:]]|^)(test|demo|dummy|muster|beispiel|nicht aktiv|inaktiv|gesperrt|obsolet|veraltet|ungültig|gelöscht|obsolete|deprecated|invalid|deleted|outdated|tbd|todo)([[:>:]]|$)' FLAG 'i'
                    THEN '|Teilebezeichnung 3 enthält Platzhalter oder obsolete Begriffe'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 6: PartDesc4
            -- PART_DESC4
            -- Typen: Einheitlichkeit, Genauigkeit, Redundanz, Relevanz, Validität
            CASE
                -- Einheitlichkeit
                WHEN COALESCE(PART_DESC4, '') <> '' AND PART_DESC4 <> TRIM(PART_DESC4)
                    THEN '' --'|Teilebezeichnung 4 mit Rand-Leerzeichen'
                -- Redundanz
                WHEN COALESCE(PART_DESC4, '') LIKE_REGEXPR '\s{2,}'
                    THEN '|Teilebezeichnung 4 mit mehrfachen Leerzeichen'
                -- Validität
                WHEN COALESCE(PART_DESC4, '') LIKE_REGEXPR '[[:cntrl:]]'
                    THEN '|Teilebezeichnung 4 enthält Steuerzeichen'
                -- Genauigkeit
                WHEN LENGTH(TRIM(COALESCE(PART_DESC4, ''))) > 255
                    THEN '|Teilebezeichnung 4 länger als 255 Zeichen'
                -- Relevanz
                WHEN COALESCE(PART_DESC4, '') LIKE_REGEXPR '([[:<:]]|^)(test|demo|dummy|muster|beispiel|nicht aktiv|inaktiv|gesperrt|obsolet|veraltet|ungültig|gelöscht|obsolete|deprecated|invalid|deleted|outdated|tbd|todo)([[:>:]]|$)' FLAG 'i'
                    THEN '|Teilebezeichnung 4 enthält Platzhalter oder obsolete Begriffe'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 7: PartSearchTerm
            -- Typen: Einheitlichkeit, Relevanz, Validität, Vollständigkeit
            CASE
                -- Vollständigkeit
                WHEN part_search_term IS NULL OR TRIM(part_search_term) = ''
                    THEN '|Suchbegriff leer'
                -- Einheitlichkeit
                WHEN part_search_term <> TRIM(part_search_term)
                    THEN '|Suchbegriff mit Leerzeichen'
                -- Validität
                WHEN part_search_term NOT LIKE_REGEXPR '^[0-9\p{L}\s\-\.&]+$' FLAG 'i'
                    THEN '|Suchbegriff keine Buchstaben/Zahlen'
                -- Relevanz
                WHEN part_search_term LIKE_REGEXPR '([[:<:]]|^)(test|nicht aktiv|inaktiv|inactive|gesperrt|obsolet|veraltet|ungültig|inaktiv|gesperrt|stillgelegt|außer\s+Betrieb|abgelaufen|deaktiviert|gelöscht|archiviert|nicht\s+mehr\s+gültig|historisch|ausgelaufen|beendet|geschlossen|nicht\s+mehr\s+aktiv|ersetzt|überholt|nicht\s+mehr\s+verwendet|obsolete|deprecated|inactive|invalid|expired|deactivated|disabled|deleted|archived|closed|terminated|discontinued|retired|replaced|superseded|outdated|legacy|historical|end-of-life|phased\s+out|suspended|cancelled|canceled|void)([[:>:]]|$)' FLAG 'i'
                    THEN '|Suchbegriff enthält ungültige Wörter'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 8: PartSortDesc
            -- Typen: Einheitlichkeit, Relevanz, Validität, Vollständigkeit
            CASE
                -- Vollständigkeit
                WHEN part_sort_desc IS NULL OR TRIM(part_sort_desc) = ''
                    THEN '|Sortierbeschreibung leer'
                -- Einheitlichkeit
                WHEN part_sort_desc <> TRIM(part_sort_desc)
                    THEN '|Sortierbeschreibung mit Leerzeichen'
                -- Validität
                WHEN part_sort_desc NOT LIKE_REGEXPR '.*[A-Z0-9].*' FLAG 'i'
                    THEN '|Sortierbeschreibung keine Buchstaben/Zahlen'
                -- Relevanz
                WHEN part_sort_desc LIKE_REGEXPR '([[:<:]]|^)(test|nicht aktiv|inaktiv|inactive|gesperrt|obsolet|veraltet|ungültig|inaktiv|gesperrt|stillgelegt|außer\s+Betrieb|abgelaufen|deaktiviert|gelöscht|archiviert|nicht\s+mehr\s+gültig|historisch|ausgelaufen|beendet|geschlossen|nicht\s+mehr\s+aktiv|ersetzt|überholt|nicht\s+mehr\s+verwendet|obsolete|deprecated|inactive|invalid|expired|deactivated|disabled|deleted|archived|closed|terminated|discontinued|retired|replaced|superseded|outdated|legacy|historical|end-of-life|phased\s+out|suspended|cancelled|canceled|void)([[:>:]]|$)' FLAG 'i'
                    THEN '|Sortierbeschreibung enthält ungültige Wörter'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 9: PartGroup
            -- Validiert die Klassifizierung des Teils in Gruppen
            -- Typen: Einheitlichkeit, Validität, Vollständigkeit
            CASE
                -- Vollständigkeit
                WHEN part_group IS NULL OR TRIM(part_group) = ''
                    THEN '|Teilegruppe leer'
                -- Einheitlichkeit
                WHEN part_group <> TRIM(part_group)
                    THEN '|Teilegruppe mit Leerzeichen'
                -- Validität
                WHEN part_group <> '' AND part_group NOT LIKE_REGEXPR '^[A-Z0-9_\-]+$' FLAG 'i'
                    THEN '' --'|Teilegruppe ungültige Zeichen'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 10: PartTariffNumber
            -- Validiert die Zolltarifnummer
            -- Typen: Einheitlichkeit, Validität, Vollständigkeit
            CASE
                -- Vollständigkeit
                WHEN part_tariff_number IS NULL OR TRIM(part_tariff_number) = ''
                    THEN '' --'|Zolltarifnummer leer'
                -- Einheitlichkeit
                WHEN part_tariff_number <> TRIM(part_tariff_number)
                    THEN '|Zolltarifnummer mit Leerzeichen'
                -- Validität
                WHEN part_tariff_number NOT LIKE_REGEXPR '^\p{N}{6,12}$'
                    THEN '|Zolltarifnummer falsches Muster'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 11: PartStorageUnit
            -- Typen: Einheitlichkeit, Validität, Vollständigkeit
            CASE
                -- Vollständigkeit
                WHEN part_storage_unit IS NULL OR TRIM(part_storage_unit) = ''
                    THEN '|Lagermengeneinheit leer'
                -- Einheitlichkeit
                WHEN part_storage_unit <> TRIM(part_storage_unit)
                    THEN '|Lagermengeneinheit mit Leerzeichen'
                -- Validität
                WHEN part_storage_unit NOT LIKE_REGEXPR '^[0-9]{1,2}$'
                    THEN '' --'|Lagermengeneinheit falsches Muster'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 12: PartBOMUnit
            -- Typen: Einheitlichkeit, Validität, Vollständigkeit
            CASE
                -- Vollständigkeit
                WHEN part_b_o_m_unit IS NULL OR TRIM(TO_NVARCHAR(part_b_o_m_unit)) = ''
                    THEN '|Stücklistenmengeneinheit leer'
                -- Einheitlichkeit
                WHEN TO_NVARCHAR(part_b_o_m_unit) <> TRIM(TO_NVARCHAR(part_b_o_m_unit))
                    THEN '|Stücklistenmengeneinheit mit Leerzeichen'
                -- Validität
                WHEN part_b_o_m_unit < 0
                    THEN '' --'|Stücklistenmengeneinheit falsches Muster'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 13: PartStorageWeight
            -- Typen: Einheitlichkeit, Konsistenz, Korrektheit, Validität, Vollständigkeit
            CASE
                -- Vollständigkeit
                WHEN part_storage_weight IS NULL
                    THEN '|Lagergewicht leer'
                -- Einheitlichkeit
                WHEN TO_NVARCHAR(part_storage_weight) <> TRIM(TO_NVARCHAR(part_storage_weight))
                    THEN '|Lagergewicht mit Leerzeichen'
                -- Korrektheit
                WHEN part_storage_weight < 0
                    THEN '|Lagergewicht negativ'
                -- Vollständigkeit
                WHEN part_weight_unit IS NULL OR TRIM(part_weight_unit) = ''
                    THEN '|Gewichtseinheit leer'
                -- Einheitlichkeit
                WHEN part_weight_unit <> TRIM(part_weight_unit)
                    THEN '|Gewichtseinheit mit Leerzeichen'
                -- Validität
                WHEN part_weight_unit NOT LIKE_REGEXPR '^[0-9]{1,2}$'
                    THEN '' --'|Gewichtseinheit falsches Muster'
                -- Konsistenz
                WHEN part_storage_weight = 0 AND COALESCE(TRIM(TO_NVARCHAR(part_weight_unit)), '') <> ''
                    THEN '' --'|Gewichtseinheit vorhanden, aber Lagergewicht ist 0'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 14: PartCreationDate
            -- Validiert Erstellungsdatum des Artikelstammsatzes
            -- Typen: Aktualität, Korrektheit, Vollständigkeit
            CASE
                -- Vollständigkeit
                WHEN part_creation_date IS NULL
                    THEN '|Erstellungsdatum leer'
                -- Korrektheit
                WHEN part_creation_date > CURRENT_DATE
                    THEN '|Erstellungsdatum in Zukunft'
                -- Korrektheit
                WHEN part_creation_date < CAST('1900-01-01' AS DATE)
                    THEN '|Erstellungsdatum vor 1900'
                -- Aktualität
                WHEN DAYS_BETWEEN(part_creation_date, CURRENT_DATE) / 365 > 100
                    THEN '|Erstellungsdatum zu alt'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 15: PartCreationDate
            -- Typen: Einheitlichkeit, Validität, Vollständigkeit
            CASE
                -- Vollständigkeit
                WHEN part_creation_date IS NOT NULL AND (part_creation_user IS NULL OR TRIM(part_creation_user) = '')
                    THEN '|Erstellungsbenutzer leer'
                -- Einheitlichkeit
                WHEN part_creation_user <> TRIM(part_creation_user)
                    THEN '|Erstellungsbenutzer mit Leerzeichen'
                -- Validität
                WHEN part_creation_user IS NOT NULL AND part_creation_user NOT LIKE_REGEXPR '^[\p{L}0-9_.@-]+$'
                    THEN '|Erstellungsbenutzer ungültige Zeichen'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 16: PartChangeDate
            -- Validiert Änderungsdatum des Artikelstammsatzes
            -- Typen: Aktualität, Konsistenz, Korrektheit, Vollständigkeit
            CASE
                -- Vollständigkeit
                WHEN part_change_date IS NULL
                    THEN '|Änderungsdatum leer'
                -- Korrektheit
                WHEN part_change_date > CURRENT_DATE
                    THEN '|Änderungsdatum in Zukunft'
                -- Konsistenz
                WHEN part_change_date < part_creation_date
                    THEN '|Änderungsdatum < ERSTELLUNGSDATUM'
                -- Korrektheit
                WHEN part_change_date < CAST('1900-01-01' AS DATE)
                    THEN '|Änderungsdatum vor 1900'
                -- Aktualität
                WHEN DAYS_BETWEEN(part_change_date, CURRENT_DATE) / 365 > 100
                    THEN '|Änderungsdatum zu alt'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 17: PartChangeDate
            -- Typen: Einheitlichkeit, Validität, Vollständigkeit
            CASE
                -- Vollständigkeit
                WHEN part_change_date IS NOT NULL AND (part_change_user IS NULL OR TRIM(part_change_user) = '')
                    THEN '|Änderungsbenutzer leer'
                -- Einheitlichkeit
                WHEN part_change_user <> TRIM(part_change_user)
                    THEN '|Änderungsbenutzer mit Leerzeichen'
                -- Validität
                WHEN part_change_user IS NOT NULL AND part_change_user NOT LIKE_REGEXPR '^[\p{L}0-9_.@-]+$'
                    THEN '|Änderungsbenutzer ungültige Zeichen'
                ELSE ''
            END
        ) AS DEFICIENCY_DESCRIPTION
    FROM
        joined s
)

-- ----------------------------------------------------------------------------
-- Hauptabfrage: Formatierung der Ergebnisse
-- ----------------------------------------------------------------------------
-- Erstellt die finale Ausgabe mit allen notwendigen Metadaten für das
-- Data Quality Management System
-- ----------------------------------------------------------------------------
SELECT
    -- Kommentieren Sie die folgende Zeile aus, um alle Datensätze anzuzeigen
    -- TOP 25
    '03'                                                                AS RULENUMBER,
    'Teile-Stammdaten Datenqualitätssicherung'                          AS RULENAME,
    deficiency_description                                              AS RULEDESCRIPTION,
    LENGTH(REPLACE_REGEXPR('[^|]' IN deficiency_description WITH ''))   AS ERROREVALUATION,
    'S_Artikel'                                                         AS AREA,
    'Teil'                                                              AS RULEFIELD,
    part_i_d                                                            AS IDENTIFIER,
    REPLACE_REGEXPR(
            '\s+' IN (
                COALESCE(TRIM(part_desc1), '') || ' ' || 
                COALESCE(TRIM(part_desc2), '') || ' ' || 
                COALESCE(TRIM(part_desc3), '') || ' ' || 
                COALESCE(TRIM(part_desc4), '')
            ) WITH ' '
        )                                                               AS DESCRIPTION,
    REPLACE_REGEXPR(
            '\s+' IN (
                COALESCE(TRIM(MASTER_DATA_SUB_TYPE), '') || 
                '|<Firma>' || COALESCE(TRIM(COMPANY), '') || 
                '|<Teil>' || COALESCE(TRIM(PART_I_D), '') || 
                '|<Teilegruppe>' || COALESCE(TRIM(PART_GROUP), '') || 
                '|<Zolltarifnummer>' || COALESCE(TRIM(PART_TARIFF_NUMBER), '') || 
                '|<Lagereinheit>' || COALESCE(TRIM(PART_STORAGE_UNIT), '') || 
                '|<Archiviert>' || COALESCE(TRIM(PART_ARCHIVED), '') || 
                '|<Teilname1>' || COALESCE(TRIM(PART_DESC1), '') || 
                '|<Teilname2>' || COALESCE(TRIM(PART_DESC2), '') || 
                '|<Teilname3>' || COALESCE(TRIM(PART_DESC3), '') || 
                '|<Teilname4>' || COALESCE(TRIM(PART_DESC4), '') || 
                '|<Sortierbeschreibung>' || COALESCE(TRIM(PART_SORT_DESC), '') || 
                '|<Suchbegriff>' || COALESCE(TRIM(PART_SEARCH_TERM), '') || 
                '|<BOM_ME>' || COALESCE(CAST(PART_B_O_M_UNIT AS NVARCHAR), '') || 
                '|<Lagergewicht>' || COALESCE(CAST(PART_STORAGE_WEIGHT AS NVARCHAR), '') || 
                '|<GewichtseinheitT>' || COALESCE(TRIM(PART_WEIGHT_UNIT), '') ||
                '|<AnlageDatum>' || COALESCE(TO_NVARCHAR(PART_CREATION_DATE), '') ||
                '|<AnlageBenutzer>' || COALESCE(TO_NVARCHAR(PART_CREATION_USER), '') ||
                '|<AenderungDatum>' || COALESCE(TO_NVARCHAR(PART_CHANGE_DATE), '') ||
                '|<AenderungBenutzer>' || COALESCE(TO_NVARCHAR(PART_CHANGE_USER), '')
            ) WITH ' '
        )                                                              AS DESCRIPTION2,
    'Part'                                                              AS CATEGORY,
    CURRENT_DATE                                                        AS ANALYSISDATE,
    COMPANY                                                             AS COMPANY,
    'Teil'                                                              AS FIELDNAME,
    'paSystem'                                                          AS PERSON,
    (CASE
        WHEN DEFICIENCY_DESCRIPTION <> '' THEN 'check' ELSE 'ok'
    END)                                                                AS STATUS
    
FROM
    checks
-- Kommentieren Sie die folgende Zeile aus, um alle Datensätze anzuzeigen
-- WHERE DEFICIENCY_DESCRIPTION <> '' ORDER BY ERROREVALUATION DESC
