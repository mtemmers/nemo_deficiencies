-- ================================================================================
-- NEMO DQM Report SQL
-- Report: (DEFICIENCIES) Kunden
-- Internal Name: deficiencies_customers
-- Generiert am: 2026-07-29T14:04:02+02:00
-- Generator: nemo_deficiencies SQL generator
-- Prüfblöcke: 20
-- Regeln aktiv/inaktiv: 124 / 33
-- DQ-Typen: Vollständigkeit=20, Validität=20, Korrektheit=33, Eindeutigkeit=1, Konsistenz=6, Aktualität=4, Genauigkeit=9, Redundanz=5, Einheitlichkeit=37, Relevanz=6, Zuverlässigkeit=7, Verständlichkeit=9
-- --------------------------------------------------------------------------------
-- Checks:
--   01. ADDRESS_NAME1-3 (Kundenname) (11 aktiv / 1 inaktiv) - Einheitlichkeit, Konsistenz, Redundanz, Relevanz, Validität, Verständlichkeit, Vollständigkeit
--   02. ADDRESS_STREET (Straßenname) (14 aktiv / 0 inaktiv) - Aktualität, Einheitlichkeit, Genauigkeit, Konsistenz, Redundanz, Relevanz, Validität, Verständlichkeit, Vollständigkeit
--   03. ADDRESS_STREET_NO (Hausnummer) (9 aktiv / 1 inaktiv) - Einheitlichkeit, Genauigkeit, Redundanz, Relevanz, Validität, Verständlichkeit, Vollständigkeit
--   04. ADDRESS_SEARCH_TERM (Suchbegriff - Adresse) (6 aktiv / 2 inaktiv) - Einheitlichkeit, Relevanz, Validität, Verständlichkeit, Vollständigkeit
--   05. ADDRESS_Z_I_P_CODE (Postleitzahl) (29 aktiv / 0 inaktiv) - Einheitlichkeit, Konsistenz, Korrektheit, Validität, Vollständigkeit, Zuverlässigkeit
--   06. ADDRESS_CITY (Ort) (7 aktiv / 1 inaktiv) - Einheitlichkeit, Relevanz, Validität, Verständlichkeit, Vollständigkeit
--   07. ADDRESS_COUNTRY (Land) (6 aktiv / 1 inaktiv) - Einheitlichkeit, Validität, Vollständigkeit
--   08. ADDRESS_STATE (Bundesland) (0 aktiv / 8 inaktiv) - Aktualität, Einheitlichkeit, Genauigkeit, Korrektheit, Validität, Vollständigkeit, Zuverlässigkeit
--   09. ADDRESS_E_MAIL (E-Mail) (9 aktiv / 1 inaktiv) - Eindeutigkeit, Einheitlichkeit, Genauigkeit, Korrektheit, Redundanz, Validität, Vollständigkeit, Zuverlässigkeit
--   10. ADDRESS_TELEPHONE (Telefonnummer) (9 aktiv / 1 inaktiv) - Einheitlichkeit, Genauigkeit, Konsistenz, Korrektheit, Redundanz, Validität, Verständlichkeit, Vollständigkeit, Zuverlässigkeit
--   11. ADDRESS_U_R_L (Website) (7 aktiv / 1 inaktiv) - Einheitlichkeit, Genauigkeit, Korrektheit, Validität, Verständlichkeit, Vollständigkeit, Zuverlässigkeit
--   12. CUSTOMER_SEARCH_TERM (Suchbegriff - Kunde) (4 aktiv / 1 inaktiv) - Einheitlichkeit, Relevanz, Validität, Verständlichkeit, Vollständigkeit
--   13. CUSTOMER_INDUSTRY (Branche) (0 aktiv / 3 inaktiv) - Einheitlichkeit, Validität, Vollständigkeit
--   14. CUSTOMER_CREDIT_TERMS_DESC (Zahlungsbedingungen) (0 aktiv / 2 inaktiv) - Einheitlichkeit, Vollständigkeit
--   15. CUSTOMER_PAYMENT_METHOD (Zahlungsmethode) (0 aktiv / 2 inaktiv) - Einheitlichkeit, Vollständigkeit
--   16. CUSTOMER_PRICE_GROUP (Preisgruppe) (0 aktiv / 2 inaktiv) - Einheitlichkeit, Vollständigkeit
--   17. CUSTOMER_CREATION_DATE (Erstellungsdatum) (4 aktiv / 0 inaktiv) - Aktualität, Korrektheit, Validität, Vollständigkeit
--   18. CUSTOMER_CHANGE_DATE (Änderungsdatum) (5 aktiv / 0 inaktiv) - Aktualität, Konsistenz, Korrektheit, Validität, Vollständigkeit
--   19. CUSTOMER_CREATION_USER (Erstellungsbenutzer) (2 aktiv / 3 inaktiv) - Einheitlichkeit, Genauigkeit, Validität, Vollständigkeit, Zuverlässigkeit
--   20. CUSTOMER_CHANGE_USER (Änderungsbenutzer) (2 aktiv / 3 inaktiv) - Einheitlichkeit, Genauigkeit, Validität, Vollständigkeit, Zuverlässigkeit
-- ================================================================================
WITH customer_source AS (
    SELECT
        company,					    -- #ERP-Origin: S_Firma.Firma
        MASTER_DATA_SUB_TYPE,           -- #Typ der Stammdaten (z.B. 'CUSTOMER' für Kunden)
        address_i_d,				    -- #ERP-Origin: S_Adresse.AdressNr
        customer_i_d,				    -- #ERP-Origin: S_Kunde.Kunde
        address_city,				    -- #ERP-Origin: S_Adresse.Ort
        address_country,			    -- #ERP-Origin: S_Adresse.Staat
        address_e_mail,				    -- #ERP-Origin: S_Adresse.EMail
        address_name,				    -- #ERP-Origin: S_Adresse.Name1
        address_name2,				    -- #ERP-Origin: S_Adresse.Name2
        address_name3,				    -- #ERP-Origin: S_Adresse.Name3
        address_search_term,		    -- #ERP-Origin: S_Adresse.Suchbegriff
        address_street,				    -- #ERP-Origin: S_Adresse.Strasse
        address_street_no,			    -- #ERP-Origin: S_Adresse.Hausnummer
        address_state,					-- #ERP-Origin: S_Adresse.Bundesland
        address_telephone,			    -- #ERP-Origin: S_Adresse.Telefon
        address_u_r_l,				    -- #ERP-Origin: S_Adresse.HomePage
        address_z_i_p_code,			    -- #ERP-Origin: S_Adresse.PLZ
        customer_change_date,		    -- #ERP-Origin: S_Kunde.AenderungDatum
        customer_change_user,		    -- #ERP-Origin: S_Kunde.AenderungBenutzer
        customer_creation_date,		    -- #ERP-Origin: S_Kunde.AnlageDatum
        customer_creation_user,		    -- #ERP-Origin: S_Kunde.AnlageBenutzer
        customer_credit_terms_desc,	    -- #ERP-Origin: S_ZahlZielSpr.Bezeichnung
        customer_industry,			    -- #ERP-Origin: S_Kunde.Branche
        customer_payment_method,	    -- #ERP-Origin: S_Kunde.ZahlungsArt
        customer_price_group,		    -- #ERP-Origin: S_Kunde.PreisGruppe
        customer_search_term		    -- #ERP-Origin: S_Kunde.Suchbegriff
    FROM
        $schema.$table
    WHERE
        UPPER(TRIM(MASTER_DATA_SUB_TYPE)) = 'CUSTOMER'
),
-- ----------------------------------------------------------------------------
-- CTE 2: PROZESSRELEVANTE KUNDEN (process_source)
-- Identifiziert Kunden, die in Geschäftsprozessen tatsächlich verwendet werden
-- ----------------------------------------------------------------------------
process_source AS (
    SELECT DISTINCT
        TRIM(CAST(COMPANY AS NVARCHAR(256))) AS COMPANY,
        TRIM(CAST(CUSTOMER_I_D AS NVARCHAR(256))) AS CUSTOMER_I_D
    FROM
        $schema."pa_export"
    WHERE
        CUSTOMER_I_D IS NOT NULL
),

-- ----------------------------------------------------------------------------
-- CTE 3: GEFILTERTE KUNDEN (joined)
-- Verknüpft Stammdaten mit prozessrelevanten Kunden (INNER JOIN)
-- Ergebnis: Nur Kunden, die auch in Prozessen verwendet werden
-- ----------------------------------------------------------------------------
joined AS (
    SELECT
        c.*
    FROM
        customer_source c
        INNER JOIN process_source p ON c.COMPANY = p.COMPANY
        AND c.CUSTOMER_I_D = p.CUSTOMER_I_D
),

-- ----------------------------------------------------------------------------
-- CTE 4: DATENQUALITÄTSPRÜFUNGEN (checks)
-- Führt umfassende Validierungen für alle relevanten Felder durch
-- ----------------------------------------------------------------------------
checks AS (
    SELECT
        j.*,
        (
            -- ================================================================
            -- PRÜFUNG 1: AddressName
            -- Validiert die kombinierten Namensfelder des Kundennamen aus der S_Adresse
            -- Typen: Einheitlichkeit, Konsistenz, Redundanz, Relevanz, Validität, Verständlichkeit, Vollständigkeit
            CASE
                -- Vollständigkeit
                WHEN COALESCE(TRIM(ADDRESS_NAME), '') = '' AND COALESCE(TRIM(ADDRESS_NAME2), '') = '' AND COALESCE(TRIM(ADDRESS_NAME3), '') = ''
                    THEN '|Name 1-3: Leer'
                -- Einheitlichkeit
                WHEN ADDRESS_NAME <> TRIM(ADDRESS_NAME) OR ADDRESS_NAME2 <> TRIM(ADDRESS_NAME2) OR ADDRESS_NAME3 <> TRIM(ADDRESS_NAME3)
                    THEN '' --'|Name 1-3: Ungültige Leerzeichen'
                -- Validität
                WHEN COALESCE(ADDRESS_NAME, '') NOT LIKE_REGEXPR '[\p{L}]' FLAG 'i' AND COALESCE(ADDRESS_NAME2, '') NOT LIKE_REGEXPR '[\p{L}]' FLAG 'i' AND COALESCE(ADDRESS_NAME3, '') NOT LIKE_REGEXPR '[\p{L}]' FLAG 'i'
                    THEN '|Name 1-3: Keine Buchstaben'
                -- Validität
                WHEN (COALESCE(ADDRESS_NAME, '') <> '' AND ADDRESS_NAME NOT LIKE_REGEXPR '^[\p{L}\p{N}\s\.\-&''()/,]+$' FLAG 'i') OR (COALESCE(ADDRESS_NAME2, '') <> '' AND ADDRESS_NAME2 NOT LIKE_REGEXPR '^[\p{L}\p{N}\s\.\-&''()/,]+$' FLAG 'i') OR (COALESCE(ADDRESS_NAME3, '') <> '' AND ADDRESS_NAME3 NOT LIKE_REGEXPR '^[\p{L}\p{N}\s\.\-&''()/,]+$' FLAG 'i')
                    THEN '|Name 1-3: Ungültige Zeichen'
                -- Redundanz
                WHEN COALESCE(ADDRESS_NAME, '') LIKE_REGEXPR '[\-&,/.]{2,}' OR COALESCE(ADDRESS_NAME2, '') LIKE_REGEXPR '[\-&,/.]{2,}' OR COALESCE(ADDRESS_NAME3, '') LIKE_REGEXPR '[\-&,/.]{2,}'
                    THEN '|Name 1-3: Mehrfache Sonderzeichen'
                -- Verständlichkeit
                WHEN COALESCE(ADDRESS_NAME, '') LIKE_REGEXPR '^[\-&,./()\s]|[\-&,./()\s]$' OR COALESCE(ADDRESS_NAME2, '') LIKE_REGEXPR '^[\-&,./()\s]|[\-&,./()\s]$' OR COALESCE(ADDRESS_NAME3, '') LIKE_REGEXPR '^[\-&,./()\s]|[\-&,./()\s]$'
                    THEN '|Name 1-3: Ungültiger Anfang/Ende'
                -- Relevanz
                WHEN COALESCE(ADDRESS_NAME, '') LIKE_REGEXPR '([[:<:]]|^)(test|nicht aktiv|inaktiv|inactive|gesperrt|obsolet|veraltet|ungültig|stillgelegt|ausser\s+Betrieb|abgelaufen|deaktiviert|gelöscht|archiviert|nicht\s+mehr\s+gültig|historisch|ausgelaufen|beendet|geschlossen|nicht\s+mehr\s+aktiv|ersetzt|überholt|nicht\s+mehr\s+verwendet|obsolete|deprecated|inactive|invalid|expired|deactivated|disabled|deleted|archived|closed|terminated|discontinüd|retired|replaced|superseded|outdated|legacy|historical|end-of-life|phased\s+out|suspended|cancelled|canceled|void)([[:>:]]|$)' FLAG 'i' OR COALESCE(ADDRESS_NAME2, '') LIKE_REGEXPR '([[:<:]]|^)(test|nicht aktiv|inaktiv|inactive|gesperrt|obsolet|veraltet|ungültig|stillgelegt|ausser\s+Betrieb|abgelaufen|deaktiviert|gelöscht|archiviert|nicht\s+mehr\s+gültig|historisch|ausgelaufen|beendet|geschlossen|nicht\s+mehr\s+aktiv|ersetzt|überholt|nicht\s+mehr\s+verwendet|obsolete|deprecated|inactive|invalid|expired|deactivated|disabled|deleted|archived|closed|terminated|discontinüd|retired|replaced|superseded|outdated|legacy|historical|end-of-life|phased\s+out|suspended|cancelled|canceled|void)([[:>:]]|$)' FLAG 'i' OR COALESCE(ADDRESS_NAME3, '') LIKE_REGEXPR '([[:<:]]|^)(test|nicht aktiv|inaktiv|inactive|gesperrt|obsolet|veraltet|ungültig|stillgelegt|ausser\s+Betrieb|abgelaufen|deaktiviert|gelöscht|archiviert|nicht\s+mehr\s+gültig|historisch|ausgelaufen|beendet|geschlossen|nicht\s+mehr\s+aktiv|ersetzt|überholt|nicht\s+mehr\s+verwendet|obsolete|deprecated|inactive|invalid|expired|deactivated|disabled|deleted|archived|closed|terminated|discontinüd|retired|replaced|superseded|outdated|legacy|historical|end-of-life|phased\s+out|suspended|cancelled|canceled|void)([[:>:]]|$)' FLAG 'i'
                    THEN '|Name 1-3: Obsolet'
                -- Einheitlichkeit
                WHEN (ADDRESS_NAME <> TRIM(COALESCE(ADDRESS_NAME, '')) OR ADDRESS_NAME2 <> TRIM(COALESCE(ADDRESS_NAME2, '')) OR ADDRESS_NAME3 <> TRIM(COALESCE(ADDRESS_NAME3, ''))) AND (COALESCE(TRIM(ADDRESS_NAME), '') <> '' OR COALESCE(TRIM(ADDRESS_NAME2), '') <> '' OR COALESCE(TRIM(ADDRESS_NAME3), '') <> '')
                    THEN '|Name 1-3: Uneinheitliche Leerzeichen'
                -- Konsistenz
                WHEN (COALESCE(ADDRESS_NAME, '') LIKE_REGEXPR '[ÄÖÜäöüß]' OR COALESCE(ADDRESS_NAME2, '') LIKE_REGEXPR '[ÄÖÜäöüß]' OR COALESCE(ADDRESS_NAME3, '') LIKE_REGEXPR '[ÄÖÜäöüß]') AND (COALESCE(ADDRESS_NAME, '') LIKE_REGEXPR '(AE|OE|UE|SS)' FLAG 'i' OR COALESCE(ADDRESS_NAME2, '') LIKE_REGEXPR '(AE|OE|UE|SS)' FLAG 'i' OR COALESCE(ADDRESS_NAME3, '') LIKE_REGEXPR '(AE|OE|UE|SS)' FLAG 'i')
                    THEN '|Name 1-3: Uneinheitliche Umlaut-/ss-Schreibweise'
                -- Einheitlichkeit
                WHEN (COALESCE(ADDRESS_NAME, '') LIKE_REGEXPR '(^|[[:space:],])G\\s*\\.?\\s*M\\s*\\.?\\s*B\\s*\\.?\\s*H\\s*\\.?($|[[:space:],])' FLAG 'i' AND COALESCE(ADDRESS_NAME, '') NOT LIKE_REGEXPR '(^|[[:space:],])GmbH($|[[:space:],])' FLAG 'i') OR (COALESCE(ADDRESS_NAME2, '') LIKE_REGEXPR '(^|[[:space:],])G\\s*\\.?\\s*M\\s*\\.?\\s*B\\s*\\.?\\s*H\\s*\\.?($|[[:space:],])' FLAG 'i' AND COALESCE(ADDRESS_NAME2, '') NOT LIKE_REGEXPR '(^|[[:space:],])GmbH($|[[:space:],])' FLAG 'i') OR (COALESCE(ADDRESS_NAME3, '') LIKE_REGEXPR '(^|[[:space:],])G\\s*\\.?\\s*M\\s*\\.?\\s*B\\s*\\.?\\s*H\\s*\\.?($|[[:space:],])' FLAG 'i' AND COALESCE(ADDRESS_NAME3, '') NOT LIKE_REGEXPR '(^|[[:space:],])GmbH($|[[:space:],])' FLAG 'i')
                    THEN '|Name 1-3: Rechtsform uneinheitlich (GmbH)'
                -- Einheitlichkeit
                WHEN (COALESCE(ADDRESS_NAME, '') LIKE_REGEXPR 'G\\s*\\.?\\s*M\\s*\\.?\\s*B\\s*\\.?\\s*H\\s*(&|UND)\\s*CO\\s*\\.?\\s*K\\s*\\.?\\s*G\\s*\\.?' FLAG 'i' AND COALESCE(ADDRESS_NAME, '') NOT LIKE_REGEXPR 'GmbH\\s*&\\s*Co\\.\\s*KG' FLAG 'i') OR (COALESCE(ADDRESS_NAME2, '') LIKE_REGEXPR 'G\\s*\\.?\\s*M\\s*\\.?\\s*B\\s*\\.?\\s*H\\s*(&|UND)\\s*CO\\s*\\.?\\s*K\\s*\\.?\\s*G\\s*\\.?' FLAG 'i' AND COALESCE(ADDRESS_NAME2, '') NOT LIKE_REGEXPR 'GmbH\\s*&\\s*Co\\.\\s*KG' FLAG 'i') OR (COALESCE(ADDRESS_NAME3, '') LIKE_REGEXPR 'G\\s*\\.?\\s*M\\s*\\.?\\s*B\\s*\\.?\\s*H\\s*(&|UND)\\s*CO\\s*\\.?\\s*K\\s*\\.?\\s*G\\s*\\.?' FLAG 'i' AND COALESCE(ADDRESS_NAME3, '') NOT LIKE_REGEXPR 'GmbH\\s*&\\s*Co\\.\\s*KG' FLAG 'i')
                    THEN '|Name 1-3: Rechtsform uneinheitlich (GmbH & Co. KG)'
                -- Einheitlichkeit
                WHEN (COALESCE(ADDRESS_NAME, '') LIKE_REGEXPR '(^|[[:space:],])(A\\s*\\.?\\s*G|K\\s*\\.?\\s*G|O\\s*\\.?\\s*H\\s*\\.?\\s*G)\\s*\\.?($|[[:space:],])' FLAG 'i' AND COALESCE(ADDRESS_NAME, '') NOT LIKE_REGEXPR '(^|[[:space:],])(AG|KG|OHG)($|[[:space:],])') OR (COALESCE(ADDRESS_NAME2, '') LIKE_REGEXPR '(^|[[:space:],])(A\\s*\\.?\\s*G|K\\s*\\.?\\s*G|O\\s*\\.?\\s*H\\s*\\.?\\s*G)\\s*\\.?($|[[:space:],])' FLAG 'i' AND COALESCE(ADDRESS_NAME2, '') NOT LIKE_REGEXPR '(^|[[:space:],])(AG|KG|OHG)($|[[:space:],])') OR (COALESCE(ADDRESS_NAME3, '') LIKE_REGEXPR '(^|[[:space:],])(A\\s*\\.?\\s*G|K\\s*\\.?\\s*G|O\\s*\\.?\\s*H\\s*\\.?\\s*G)\\s*\\.?($|[[:space:],])' FLAG 'i' AND COALESCE(ADDRESS_NAME3, '') NOT LIKE_REGEXPR '(^|[[:space:],])(AG|KG|OHG)($|[[:space:],])')
                    THEN '|Name 1-3: Rechtsform uneinheitlich (AG/KG/OHG)'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 2: AddressStreet
            -- Validiert Straßenname aus der Adresse des Kunden
            -- Typen: Aktualität, Einheitlichkeit, Genauigkeit, Konsistenz, Redundanz, Relevanz, Validität, Verständlichkeit, Vollständigkeit
            CASE
                -- Vollständigkeit
                WHEN TRIM(ADDRESS_STREET) = '' OR ADDRESS_STREET IS NULL
                    THEN '|Straße: Leer'
                -- Einheitlichkeit
                WHEN ADDRESS_STREET <> TRIM(ADDRESS_STREET)
                    THEN '|Straße: Ungültige Leerzeichen'
                -- Einheitlichkeit
                WHEN ADDRESS_STREET LIKE_REGEXPR '[[:space:]]{2,}'
                    THEN '|Straße: Mehrfache Leerzeichen'
                -- Validität
                WHEN ADDRESS_STREET NOT LIKE_REGEXPR '[\p{L}]' FLAG 'i'
                    THEN '|Straße: Keine Buchstaben'
                -- Validität
                WHEN ADDRESS_STREET NOT LIKE_REGEXPR '^[\p{L}\p{N}\s\.\-''&()/,]+$' FLAG 'i'
                    THEN '|Straße: Ungültige Zeichen'
                -- Genauigkeit
                WHEN LENGTH(TRIM(ADDRESS_STREET)) < 2
                    THEN '|Straße: Zu kurz'
                -- Redundanz
                WHEN ADDRESS_STREET LIKE_REGEXPR '[\.\-/,]{2,}'
                    THEN '|Straße: Mehrfache Sonderzeichen'
                -- Verständlichkeit
                WHEN ADDRESS_STREET LIKE_REGEXPR '^[\-\.,/ ]|[\-\.,/ ]$'
                    THEN '|Straße: Ungültiger Anfang/Ende'
                -- Konsistenz
                WHEN ADDRESS_COUNTRY IN ('D', 'DE', 'AT') AND ADDRESS_STREET LIKE_REGEXPR 'STRASSE([[:>:]]|$)' FLAG 'i'
                    THEN '|Straße: Für DE/AT wird "Straße" statt "Strasse" erwartet'
                -- Konsistenz
                WHEN ADDRESS_COUNTRY = 'CH' AND ADDRESS_STREET LIKE_REGEXPR 'ß'
                    THEN '|Straße: Für CH wird "ss" statt "ß" erwartet'
                -- Verständlichkeit
                WHEN ADDRESS_COUNTRY IN ('D', 'DE', 'AT') AND ADDRESS_STREET LIKE_REGEXPR 'STR\.?([[:>:]]|$)' FLAG 'i'
                    THEN '|Straße: Abkürzung "Str." sollte ausgeschrieben werden'
                -- Einheitlichkeit
                WHEN ADDRESS_STREET LIKE_REGEXPR '\s+-\s+|\s+/\s+'
                    THEN '|Straße: Uneinheitliche Separator-Schreibweise'
                -- Relevanz
                WHEN TRIM(ADDRESS_STREET) LIKE_REGEXPR '^(N/?A|N\.?\s?V\.?|KEINE|UNBEKANNT|OHNE|NICHT\s+BEKANNT)$' FLAG 'i'
                    THEN '|Straße: Platzhalterwert'
                -- Aktualität
                WHEN ADDRESS_STREET LIKE_REGEXPR '([[:<:]]|^)(test|nicht aktiv|inaktiv|inactive|gesperrt|obsolet|veraltet|ungültig|inaktiv|gesperrt|stillgelegt|ausser\s+Betrieb|abgelaufen|deaktiviert|gelöscht|archiviert|nicht\s+mehr\s+gültig|historisch|ausgelaufen|beendet|geschlossen|nicht\s+mehr\s+aktiv|ersetzt|überholt|nicht\s+mehr\s+verwendet|obsolete|deprecated|inactive|invalid|expired|deactivated|disabled|deleted|archived|closed|terminated|discontinüd|retired|replaced|superseded|outdated|legacy|historical|end-of-life|phased\s+out|suspended|cancelled|canceled|void)([[:>:]]|$)' FLAG 'i'
                    THEN '|Straße: Obsolet'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 3: AddressStreetNo
            -- Validiert Hausnummer aus der Adresse des Kunden
            -- Typen: Einheitlichkeit, Genauigkeit, Redundanz, Relevanz, Validität, Verständlichkeit, Vollständigkeit
            CASE
                -- Vollständigkeit
                WHEN TRIM(ADDRESS_STREET_NO) = '' OR ADDRESS_STREET_NO IS NULL
                    THEN '' --'|Hausnummer: Leer'
                -- Einheitlichkeit
                WHEN ADDRESS_STREET_NO <> TRIM(ADDRESS_STREET_NO)
                    THEN '|Hausnummer: Ungültige Leerzeichen'
                -- Relevanz
                WHEN ADDRESS_STREET_NO LIKE_REGEXPR '^n\.?a\.?$' FLAG 'i'
                    THEN '|Hausnummer: Obsolet (n.a.)'
                -- Redundanz
                WHEN ADDRESS_STREET_NO LIKE_REGEXPR '[/\-]{2,}'
                    THEN '|Hausnummer: Mehrfache Separatoren'
                -- Verständlichkeit
                WHEN ADDRESS_STREET_NO LIKE_REGEXPR '\.'
                    THEN '|Hausnummer: Punkte nicht erlaubt (verwende / oder -)'
                -- Validität
                WHEN ADDRESS_STREET_NO NOT LIKE_REGEXPR '[\p{N}]'
                    THEN '|Hausnummer: Keine Zahlen'
                -- Validität
                WHEN ADDRESS_STREET_NO NOT LIKE_REGEXPR '^\d+[A-Za-z]?([/\-]\d+[A-Za-z]?)*$'
                    THEN '|Hausnummer: Ungültiges Format'
                -- Einheitlichkeit
                WHEN ADDRESS_STREET_NO LIKE_REGEXPR '(^|[/\-])\d+[a-z]($|[/\-])'
                    THEN '|Hausnummer: Suffix sollte Großbuchstabe sein (z. B. 12A statt 12a)'
                -- Einheitlichkeit
                WHEN ADDRESS_STREET_NO LIKE_REGEXPR '^0+\d'
                    THEN '|Hausnummer: Führende Nullen uneinheitlich'
                -- Genauigkeit
                WHEN LENGTH(TRIM(ADDRESS_STREET_NO)) > 10
                    THEN '|Hausnummer: Zu lang'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 4: AddressSearchTerm
            -- Validiert Suchbegriff aus der Adresse des Kunden
            -- Typen: Einheitlichkeit, Relevanz, Validität, Verständlichkeit, Vollständigkeit
            CASE
                -- Vollständigkeit
                WHEN TRIM(ADDRESS_SEARCH_TERM) = '' OR ADDRESS_SEARCH_TERM IS NULL
                    THEN '' --'|Adresse Suchbegriff leer'
                -- Einheitlichkeit
                WHEN ADDRESS_SEARCH_TERM != TRIM(ADDRESS_SEARCH_TERM)
                    THEN '|Adresse Suchbegriff: Uneinheitliche Rand-Leerzeichen'
                -- Einheitlichkeit
                WHEN ADDRESS_SEARCH_TERM LIKE_REGEXPR '\s{2,}'
                    THEN '|Adresse Suchbegriff: Mehrfache Leerzeichen'
                -- Einheitlichkeit
                WHEN ADDRESS_SEARCH_TERM <> UPPER(ADDRESS_SEARCH_TERM) AND ADDRESS_SEARCH_TERM LIKE_REGEXPR '[\p{L}]' FLAG 'i'
                    THEN '' --'|Adresse Suchbegriff: Uneinheitliche Groß-/Kleinschreibung'
                -- Einheitlichkeit
                WHEN ADDRESS_SEARCH_TERM LIKE_REGEXPR '[ÄÖÜäöüß]' AND ADDRESS_SEARCH_TERM LIKE_REGEXPR '(AE|OE|UE|SS)' FLAG 'i'
                    THEN '|Adresse Suchbegriff: Uneinheitliche Umlaut-/ss-Schreibweise'
                -- Verständlichkeit
                WHEN ADDRESS_SEARCH_TERM NOT LIKE_REGEXPR '[\p{L}]' FLAG 'i'
                    THEN '|Adresse Suchbegriff: Keine Buchstaben'
                -- Validität
                WHEN ADDRESS_SEARCH_TERM LIKE_REGEXPR '[^0-9\p{L}\s-]' FLAG 'i'
                    THEN '|Adresse Suchbegriff: Ungültige Zeichen'
                -- Relevanz
                WHEN ADDRESS_SEARCH_TERM LIKE_REGEXPR '([[:<:]]|^)(test|nicht aktiv|inaktiv|inactive|gesperrt|obsolet|veraltet|ungültig|inaktiv|gesperrt|stillgelegt|ausser\s+Betrieb|abgelaufen|deaktiviert|gelöscht|archiviert|nicht\s+mehr\s+gültig|historisch|ausgelaufen|beendet|geschlossen|nicht\s+mehr\s+aktiv|ersetzt|überholt|nicht\s+mehr\s+verwendet|obsolete|deprecated|inactive|invalid|expired|deactivated|disabled|deleted|archived|closed|terminated|discontinüd|retired|replaced|superseded|outdated|legacy|historical|end-of-life|phased\s+out|suspended|cancelled|canceled|void)([[:>:]]|$)' FLAG 'i'
                    THEN '|Adresse Suchbegriff: Obsolet'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 5: AddressZIPCode
            -- Validiert Postleitzahl mit länderspezifischen Mustern aus der Adresse des Kunden
            -- Typen: Einheitlichkeit, Konsistenz, Korrektheit, Validität, Vollständigkeit, Zuverlässigkeit
            CASE
                -- Vollständigkeit
                WHEN TRIM(ADDRESS_Z_I_P_CODE) = '' OR ADDRESS_Z_I_P_CODE IS NULL
                    THEN '|PLZ: Leer'
                -- Einheitlichkeit
                WHEN ADDRESS_Z_I_P_CODE != TRIM(ADDRESS_Z_I_P_CODE)
                    THEN '|PLZ: Mit Leerzeichen'
                -- Validität
                WHEN ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '[\p{N}]'
                    THEN '|PLZ: Keine Zahlen'
                -- Konsistenz
                WHEN ADDRESS_COUNTRY = 'NL' AND TRIM(ADDRESS_Z_I_P_CODE) <> '' AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[\p{N}]{4}[\s]?[A-Za-z]{2}$'
                    THEN '|PLZ: Muster <> NL'
                -- Korrektheit
                WHEN ADDRESS_COUNTRY = 'PL' AND TRIM(ADDRESS_Z_I_P_CODE) <> '' AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[\p{N}]{2}-?[\p{N}]{3}$'
                    THEN '|PLZ: Muster <> PL'
                -- Korrektheit
                WHEN ADDRESS_COUNTRY = 'PT' AND TRIM(ADDRESS_Z_I_P_CODE) <> '' AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[\p{N}]{4}-?[\p{N}]{3}$'
                    THEN '|PLZ: Muster <> PT'
                -- Korrektheit
                WHEN ADDRESS_COUNTRY = 'GB' AND TRIM(ADDRESS_Z_I_P_CODE) <> '' AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[A-Za-z]{1,2}[\p{N}][A-Za-z0-9]?[\s]?[\p{N}][A-Za-z]{2}$'
                    THEN '|PLZ: Muster <> GB'
                -- Korrektheit
                WHEN ADDRESS_COUNTRY = 'CA' AND TRIM(ADDRESS_Z_I_P_CODE) <> '' AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[A-Za-z][\p{N}][A-Za-z][\s]?[\p{N}][A-Za-z][\p{N}]$'
                    THEN '|PLZ: Muster <> CA'
                -- Korrektheit
                WHEN ADDRESS_COUNTRY = 'JP' AND TRIM(ADDRESS_Z_I_P_CODE) <> '' AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[\p{N}]{3}-?[\p{N}]{4}$'
                    THEN '|PLZ: Muster <> JP'
                -- Korrektheit
                WHEN ADDRESS_COUNTRY = 'TW' AND TRIM(ADDRESS_Z_I_P_CODE) <> '' AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[\p{N}]{6}$'
                    THEN '|PLZ: Muster <> TW'
                -- Korrektheit
                WHEN ADDRESS_COUNTRY = 'BR' AND TRIM(ADDRESS_Z_I_P_CODE) <> '' AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^([\p{N}]{8}|[\p{N}]{5}-[\p{N}]{3})$'
                    THEN '|PLZ: Muster <> BR'
                -- Korrektheit
                WHEN ADDRESS_COUNTRY = 'IE' AND TRIM(ADDRESS_Z_I_P_CODE) <> '' AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[A-Za-z][0-9A-Za-z][0-9A-Za-z][\s]?[0-9A-Za-z]{4}$'
                    THEN '|PLZ: Muster <> IE'
                -- Korrektheit
                WHEN ADDRESS_COUNTRY = 'AR' AND TRIM(ADDRESS_Z_I_P_CODE) <> '' AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^([A-Za-z][\p{N}]{4}[A-Za-z]{3}|[\p{N}]{4})$'
                    THEN '|PLZ: Muster <> AR'
                -- Korrektheit
                WHEN ADDRESS_COUNTRY = 'CZ' AND TRIM(ADDRESS_Z_I_P_CODE) <> '' AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[\p{N}]{3}[\s]?[\p{N}]{2}$'
                    THEN '|PLZ: Muster <> CZ'
                -- Korrektheit
                WHEN ADDRESS_COUNTRY = 'SK' AND TRIM(ADDRESS_Z_I_P_CODE) <> '' AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[\p{N}]{3}[\s]?[\p{N}]{2}$'
                    THEN '|PLZ: Muster <> SK'
                -- Korrektheit
                WHEN ADDRESS_COUNTRY IN ('SE', 'GR') AND TRIM(ADDRESS_Z_I_P_CODE) <> '' AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[\p{N}]{3}[\s]?[\p{N}]{2}$'
                    THEN '|PLZ: Muster <>'
                -- Korrektheit
                WHEN ADDRESS_COUNTRY = 'US' AND TRIM(ADDRESS_Z_I_P_CODE) <> '' AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[\p{N}]{5}(-[\p{N}]{4})?$'
                    THEN '|PLZ: Muster <> US'
                -- Korrektheit
                WHEN ADDRESS_COUNTRY = 'LV' AND TRIM(ADDRESS_Z_I_P_CODE) <> '' AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^([Ll][Vv][-–])?[\p{N}]{4}$'
                    THEN '|PLZ: Muster <> LV'
                -- Korrektheit
                WHEN ADDRESS_COUNTRY = 'VE' AND TRIM(ADDRESS_Z_I_P_CODE) <> '' AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[\p{N}]{4}(-[A-Za-z])?$'
                    THEN '|PLZ: Muster <> VE'
                -- Korrektheit
                WHEN ADDRESS_COUNTRY = 'KZ' AND TRIM(ADDRESS_Z_I_P_CODE) <> '' AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^([\p{N}]{6}|[A-Za-z][\p{N}]{2}[A-Za-z][\p{N}][A-Za-z][\p{N}])$'
                    THEN '|PLZ: Muster <> KZ'
                -- Korrektheit
                WHEN ADDRESS_COUNTRY = 'EG' AND TRIM(ADDRESS_Z_I_P_CODE) <> '' AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^([\p{N}]{5}|[\p{N}]{7})$'
                    THEN '|PLZ: Muster <> EG'
                -- Korrektheit
                WHEN ADDRESS_COUNTRY = 'MM' AND TRIM(ADDRESS_Z_I_P_CODE) <> '' AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^([\p{N}]{5}|[\p{N}]{7})$'
                    THEN '|PLZ: Muster <> MM'
                -- Korrektheit
                WHEN ADDRESS_COUNTRY IN ('D', 'DE', 'ES', 'FR', 'IT', 'MX', 'MA', 'DZ', 'TR', 'UA', 'TH', 'MY', 'PE', 'JO', 'SA', 'GT', 'HN', 'NI', 'CR', 'LT', 'BA', 'ME', 'LA', 'NP', 'VN') AND TRIM(ADDRESS_Z_I_P_CODE) <> '' AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[\p{N}]{5}$'
                    THEN '|PLZ: 5 Zahlen erwartet'
                -- Korrektheit
                WHEN ADDRESS_COUNTRY IN ('AT', 'CH', 'DK', 'NO', 'BE', 'LU', 'LI', 'AU', 'PH', 'MK', 'SV', 'PA', 'GE', 'TN') AND TRIM(ADDRESS_Z_I_P_CODE) <> '' AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[\p{N}]{4}$'
                    THEN '|PLZ: 4 Zahlen erwartet'
                -- Korrektheit
                WHEN ADDRESS_COUNTRY IN ('RU', 'CN', 'IN', 'KG', 'UZ', 'TJ', 'TM', 'BY', 'SG', 'CO', 'KH') AND TRIM(ADDRESS_Z_I_P_CODE) <> '' AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[\p{N}]{6}$'
                    THEN '|PLZ: 6 Zahlen erwartet'
                -- Korrektheit
                WHEN ADDRESS_COUNTRY IN ('IR') AND TRIM(ADDRESS_Z_I_P_CODE) <> '' AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[\p{N}]{10}$'
                    THEN '|PLZ: 10 Zahlen erwartet'
                -- Korrektheit
                WHEN ADDRESS_COUNTRY IN ('IS') AND TRIM(ADDRESS_Z_I_P_CODE) <> '' AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[\p{N}]{3}$'
                    THEN '|PLZ: 3 Zahlen erwartet'
                -- Korrektheit
                WHEN ADDRESS_COUNTRY IN ('CL') AND TRIM(ADDRESS_Z_I_P_CODE) <> '' AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[\p{N}]{7}$'
                    THEN '|PLZ: 7 Zahlen erwartet'
                -- Zuverlässigkeit
                WHEN ADDRESS_Z_I_P_CODE LIKE_REGEXPR '(00000|99999)'
                    THEN '|PLZ: Testwert'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 6: AddressCity
            -- Validiert Ortsname aus der Adresse des Kunden
            -- Typen: Einheitlichkeit, Relevanz, Validität, Verständlichkeit, Vollständigkeit
            CASE
                -- Vollständigkeit
                WHEN TRIM(ADDRESS_CITY) = '' OR ADDRESS_CITY IS NULL
                    THEN '|Ort: Leer'
                -- Einheitlichkeit
                WHEN ADDRESS_CITY != TRIM(ADDRESS_CITY)
                    THEN '|Ort: Ungültige Leerzeichen'
                -- Verständlichkeit
                WHEN ADDRESS_CITY NOT LIKE_REGEXPR '[\p{L}]' FLAG 'i'
                    THEN '|Ort: Keine Buchstaben'
                -- Validität
                WHEN ADDRESS_CITY NOT LIKE_REGEXPR '^[\p{L}\p{N}\s\.\-'',\/'':&\(\)]*$'
                    THEN '|Ort: Ungültig'
                -- Einheitlichkeit
                WHEN ADDRESS_CITY LIKE_REGEXPR '\s{2,}'
                    THEN '|Ort: Mehrfache Leerzeichen'
                -- Einheitlichkeit
                WHEN ADDRESS_CITY <> INITCAP(LOWER(ADDRESS_CITY)) AND ADDRESS_CITY LIKE_REGEXPR '[\p{L}]' FLAG 'i'
                    THEN '' --'|Ort: Uneinheitliche Groß-/Kleinschreibung'
                -- Einheitlichkeit
                WHEN ADDRESS_CITY LIKE_REGEXPR '[ÄÖÜäöüß]' AND ADDRESS_CITY LIKE_REGEXPR '(AE|OE|UE|SS)' FLAG 'i'
                    THEN '|Ort: Uneinheitliche Umlaut-/ss-Schreibweise'
                -- Relevanz
                WHEN ADDRESS_CITY LIKE_REGEXPR '([[:<:]]|^)(test|nicht aktiv|inaktiv|inactive|gesperrt|obsolet|veraltet|ungültig|inaktiv|gesperrt|stillgelegt|ausser\s+Betrieb|abgelaufen|deaktiviert|gelöscht|archiviert|nicht\s+mehr\s+gültig|historisch|ausgelaufen|beendet|geschlossen|nicht\s+mehr\s+aktiv|ersetzt|überholt|nicht\s+mehr\s+verwendet|obsolete|deprecated|inactive|invalid|expired|deactivated|disabled|deleted|archived|closed|terminated|discontinüd|retired|replaced|superseded|outdated|legacy|historical|end-of-life|phased\s+out|suspended|cancelled|canceled|void)([[:>:]]|$)' FLAG 'i'
                    THEN '|Ort: Obsolet'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 7: AddressCountry
            -- Validiert Ländercode (ISO 3166-1 alpha-2) aus der Adresse des Kunden
            -- Typen: Einheitlichkeit, Validität, Vollständigkeit
            CASE
                -- Vollständigkeit
                WHEN TRIM(ADDRESS_COUNTRY) = '' OR ADDRESS_COUNTRY IS NULL
                    THEN '|Land: Leer'
                -- Einheitlichkeit
                WHEN ADDRESS_COUNTRY != TRIM(ADDRESS_COUNTRY)
                    THEN '|Land: Mit Leerzeichen'
                -- Einheitlichkeit
                WHEN UPPER(TRIM(ADDRESS_COUNTRY)) = 'D'
                    THEN '' --'|Land: Uneinheitlicher Code (nutze DE statt D)'
                -- Einheitlichkeit
                WHEN UPPER(TRIM(ADDRESS_COUNTRY)) = 'UK'
                    THEN '|Land: Uneinheitlicher Code (nutze GB statt UK)'
                -- Einheitlichkeit
                WHEN UPPER(TRIM(ADDRESS_COUNTRY)) LIKE_REGEXPR '^[A-Z]{3}$'
                    THEN '|Land: 3-stelliger Code (nutze ISO-2)'
                -- Einheitlichkeit
                WHEN ADDRESS_COUNTRY <> UPPER(ADDRESS_COUNTRY)
                    THEN '|Land: Sollte Großbuchstaben enthalten'
                -- Validität
                WHEN ADDRESS_COUNTRY NOT LIKE_REGEXPR '^[A-Z]{2}$'
                    THEN '|Land: Ungültiger ISO-2-Code'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 8: AddressState
            -- Validiert Bundesland-Code des Kunden
            -- Typen: Aktualität, Einheitlichkeit, Genauigkeit, Korrektheit, Validität, Vollständigkeit, Zuverlässigkeit
            CASE
                -- Vollständigkeit
                WHEN TRIM(address_state) = '' OR address_state IS NULL
                    THEN '' --'|Bundesland-Code leer'
                -- Einheitlichkeit
                WHEN address_state != TRIM(address_state)
                    THEN '' --'|Bundesland-Code mit Leerzeichen'
                -- Genauigkeit
                WHEN LENGTH(TRIM(address_state)) <> 3
                    THEN '' --'|Bundesland-Code nicht exakt 3 Zeichen'
                -- Validität
                WHEN address_state NOT LIKE_REGEXPR '^[A-Za-z0-9]{3}$'
                    THEN '' --'|Bundesland-Code ungültig (nicht 3 Zeichen aus A-Z, a-z, 0-9)'
                -- Zuverlässigkeit
                WHEN address_state LIKE_REGEXPR '^[0-9]{3}$' AND address_state IN ('000', '999')
                    THEN '' --'|Bundesland-Code: Nur Nullen oder Neunen (Testwert?)'
                -- Aktualität
                WHEN address_state LIKE_REGEXPR '([[:<:]]|^)(TST|DEM|XXX|TMP|DEL|INV|TEST)([[:>:]]|$)' FLAG 'i'
                    THEN '' --'|Bundesland-Code verdächtig (Test/System-Code)'
                -- Einheitlichkeit
                WHEN address_state LIKE_REGEXPR '^[A-Za-z]{3}$' AND address_state NOT LIKE_REGEXPR '^[A-Z]{3}$'
                    THEN '' --'|Bundesland-Code: Buchstaben sollten Großbuchstaben sein'
                -- Korrektheit
                WHEN LENGTH(REPLACE_REGEXPR('[0-9]' IN address_state WITH '')) = 0 AND address_state NOT LIKE_REGEXPR '(^[0-9]{3}$)'
                    THEN '' --'|Bundesland-Code: Gemischte Zahlen und Buchstaben'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 9: AddressEMail
            -- Validiert E-Mail-Adresse aus der Adresse des Kunden
            -- Typen: Eindeutigkeit, Einheitlichkeit, Genauigkeit, Korrektheit, Redundanz, Validität, Vollständigkeit, Zuverlässigkeit
            CASE
                -- Vollständigkeit
                WHEN TRIM(ADDRESS_E_MAIL) = '' OR ADDRESS_E_MAIL IS NULL
                    THEN '' --'|E-Mail: Leer'
                -- Einheitlichkeit
                WHEN ADDRESS_E_MAIL <> TRIM(ADDRESS_E_MAIL)
                    THEN '|E-Mail: Ungültige Leerzeichen'
                -- Genauigkeit
                WHEN LENGTH(ADDRESS_E_MAIL) > 254
                    THEN '|E-Mail: Zu lang (RFC 5321: max 254 Zeichen)'
                -- Redundanz
                WHEN ADDRESS_E_MAIL LIKE_REGEXPR '\.\.'
                    THEN '|E-Mail: Enthält ".." (ungültig)'
                -- Eindeutigkeit
                WHEN (LENGTH(ADDRESS_E_MAIL) - LENGTH(REPLACE(ADDRESS_E_MAIL, '@', ''))) <> 1
                    THEN '|E-Mail: Muss genau ein @ haben'
                -- Korrektheit
                WHEN ADDRESS_E_MAIL LIKE_REGEXPR '^[._%+-]'
                    THEN '|E-Mail: Darf nicht mit . _ % + - beginnen'
                -- Korrektheit
                WHEN ADDRESS_E_MAIL LIKE_REGEXPR '[.-]@'
                    THEN '|E-Mail: Keine . oder - direkt vor @'
                -- Korrektheit
                WHEN SUBSTRING_REGEXPR('\.([^\.]+)$' IN ADDRESS_E_MAIL GROUP 1) LIKE_REGEXPR '^[0-9]+$'
                    THEN '|E-Mail: TLD darf keine reinen Zahlen sein'
                -- Validität
                WHEN ADDRESS_E_MAIL NOT LIKE_REGEXPR '^[a-zA-Z0-9]([a-zA-Z0-9._%+\-]*[a-zA-Z0-9])?@[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.([a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.)*[a-zA-Z]{2,}$' FLAG 'i'
                    THEN '|E-Mail: Ungültiges Format'
                -- Zuverlässigkeit
                WHEN ADDRESS_E_MAIL LIKE_REGEXPR '([[:<:]]|^)(test|nicht aktiv|inaktiv|inactive|gesperrt|obsolet|veraltet|ungültig|inaktiv|gesperrt|stillgelegt|ausser\s+Betrieb|abgelaufen|deaktiviert|gelöscht|archiviert|nicht\s+mehr\s+gültig|historisch|ausgelaufen|beendet|geschlossen|nicht\s+mehr\s+aktiv|ersetzt|überholt|nicht\s+mehr\s+verwendet|obsolete|deprecated|inactive|invalid|expired|deactivated|disabled|deleted|archived|closed|terminated|discontinüd|retired|replaced|superseded|outdated|legacy|historical|end-of-life|phased\s+out|suspended|cancelled|canceled|void)([[:>:]]|$)' FLAG 'i'
                    THEN '|E-Mail: Obsolet oder Test-Adresse'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 10: AddressTelephone
            -- Validiert Telefonnummer aus der Adresse des Kunden
            -- Typen: Einheitlichkeit, Genauigkeit, Konsistenz, Korrektheit, Redundanz, Validität, Verständlichkeit, Vollständigkeit, Zuverlässigkeit
            CASE
                -- Vollständigkeit
                WHEN TRIM(ADDRESS_TELEPHONE) = '' OR ADDRESS_TELEPHONE IS NULL
                    THEN '' --'|Telefon: Leer'
                -- Einheitlichkeit
                WHEN ADDRESS_TELEPHONE <> TRIM(ADDRESS_TELEPHONE)
                    THEN '|Telefon: Ungültige Leerzeichen'
                -- Verständlichkeit
                WHEN ADDRESS_TELEPHONE NOT LIKE_REGEXPR '[\p{N}]'
                    THEN '|Telefon: Keine Zahlen'
                -- Genauigkeit
                WHEN LENGTH(REPLACE_REGEXPR('[^0-9]' IN ADDRESS_TELEPHONE WITH '')) < 6
                    THEN '|Telefon: Zu kurz'
                -- Genauigkeit
                WHEN LENGTH(REPLACE_REGEXPR('[^0-9]' IN ADDRESS_TELEPHONE WITH '')) > 20
                    THEN '|Telefon: Zu lang'
                -- Validität
                WHEN ADDRESS_TELEPHONE NOT LIKE_REGEXPR '^[\d\s\-()./+]*$'
                    THEN '|Telefon: Ungültige Zeichen'
                -- Redundanz
                WHEN ADDRESS_TELEPHONE LIKE_REGEXPR '[()]{2,}|[- ]{3,}|//'
                    THEN '|Telefon: Mehrfache Separatoren'
                -- Korrektheit
                WHEN ADDRESS_TELEPHONE LIKE_REGEXPR '.+\+'
                    THEN '|Telefon: Pluszeichen ist nur am Anfang erlaubt'
                -- Konsistenz
                WHEN ADDRESS_COUNTRY IN ('D', 'DE') AND REPLACE_REGEXPR('[^0-9]' IN ADDRESS_TELEPHONE WITH '') NOT LIKE_REGEXPR '^(49|0049|0)'
                    THEN '|Telefon: Deutsche Nummer sollte mit 0, 00, oder 49 beginnen'
                -- Zuverlässigkeit
                WHEN ADDRESS_TELEPHONE LIKE_REGEXPR '([[:<:]]|^)(test|demo|123456|999999|invalid|temp|example|toll.?free)([[:>:]]|$)' FLAG 'i'
                    THEN '|Telefon: Obsolet oder Testwert'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 11: AddressURL
            -- Validiert Website-URL aus der Adresse des Kunden
            -- Typen: Einheitlichkeit, Genauigkeit, Korrektheit, Validität, Verständlichkeit, Vollständigkeit, Zuverlässigkeit
            CASE
                -- Vollständigkeit
                WHEN TRIM(ADDRESS_U_R_L) = '' OR ADDRESS_U_R_L IS NULL
                    THEN '' --'|URL: Leer'
                -- Einheitlichkeit
                WHEN ADDRESS_U_R_L <> TRIM(ADDRESS_U_R_L)
                    THEN '|URL: Mit Leerzeichen'
                -- Genauigkeit
                WHEN LENGTH(ADDRESS_U_R_L) > 2048
                    THEN '|URL: Zu lang (mehr als 2048 Zeichen)'
                -- Verständlichkeit
                WHEN ADDRESS_U_R_L NOT LIKE_REGEXPR '[\p{L}]' FLAG 'i'
                    THEN '|URL: Keine Buchstaben'
                -- Validität
                WHEN ADDRESS_U_R_L NOT LIKE_REGEXPR '^(https?:\/\/)?([a-z0-9]([a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,}(:[0-9]{1,5})?(\/.*)?$' FLAG 'i'
                    THEN '|URL: Ungültiges Format'
                -- Korrektheit
                WHEN SUBSTRING_REGEXPR('^https?://[^/]+/(.*)' IN ADDRESS_U_R_L GROUP 1) LIKE_REGEXPR '[<>"{}\[\]\\^`|]'
                    THEN '|URL: Ungültige Zeichen im Pfad'
                -- Korrektheit
                WHEN ADDRESS_U_R_L LIKE_REGEXPR '\s'
                    THEN '|URL: Leerzeichen im Pfad (sollte %20 sein)'
                -- Zuverlässigkeit
                WHEN ADDRESS_U_R_L LIKE_REGEXPR '([[:<:]]|^)(test|demo|localhost|invalid|example\.com|staging|dev|development)([[:>:]]|$)' FLAG 'i'
                    THEN '|URL: Obsolet oder Testwert'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 12: CustomerSearchTerm
            -- Validiert Kunden-Suchbegriff
            -- CUSTOMER_SEARCH_TERM
            -- Typen: Vollständigkeit, Validität, Einheitlichkeit, Relevanz, Verständlichkeit
            CASE
                -- Vollständigkeit
                WHEN TRIM(CUSTOMER_SEARCH_TERM) = '' OR CUSTOMER_SEARCH_TERM IS NULL
                    THEN '' --'|Kunde Suchbegriff leer'
                -- Einheitlichkeit
                WHEN CUSTOMER_SEARCH_TERM != TRIM(CUSTOMER_SEARCH_TERM)
                    THEN '|Kunde Suchbegriff mit Leerzeichen'
                -- Verständlichkeit
                WHEN CUSTOMER_SEARCH_TERM NOT LIKE_REGEXPR '[\p{L}\p{N}]' FLAG 'i'
                    THEN '|Kunde Suchbegriff keine Buchstaben oder Zahlen'
                -- Validität
                WHEN CUSTOMER_SEARCH_TERM NOT LIKE_REGEXPR '[0-9\p{L}\s-]' FLAG 'i'
                    THEN '|Kunde Suchbegriff ungültig'
                -- Relevanz
                WHEN CUSTOMER_SEARCH_TERM LIKE_REGEXPR '([[:<:]]|^)(test|nicht aktiv|inaktiv|inactive|gesperrt|obsolet|veraltet|ungültig|inaktiv|gesperrt|stillgelegt|außer\s+Betrieb|abgelaufen|deaktiviert|gelöscht|archiviert|nicht\s+mehr\s+gültig|historisch|ausgelaufen|beendet|geschlossen|nicht\s+mehr\s+aktiv|ersetzt|überholt|nicht\s+mehr\s+verwendet|obsolete|deprecated|inactive|invalid|expired|deactivated|disabled|deleted|archived|closed|terminated|discontinued|retired|replaced|superseded|outdated|legacy|historical|end-of-life|phased\s+out|suspended|cancelled|canceled|void)([[:>:]]|$)' FLAG 'i'
                    THEN '|Kunde Suchbegriff obsolete'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 13: CustomerIndustry
            -- Validiert Branchenschlüssel aus dem Kunden
            -- CUSTOMER_INDUSTRY
            -- Typen: Vollständigkeit, Validität, Einheitlichkeit
            CASE
                -- Vollständigkeit
                WHEN TRIM(CUSTOMER_INDUSTRY) = '' OR CUSTOMER_INDUSTRY IS NULL
                    THEN '' --'|Branche leer'
                -- Einheitlichkeit
                WHEN CUSTOMER_INDUSTRY != TRIM(CUSTOMER_INDUSTRY)
                    THEN '' --'|Branche mit Leerzeichen'
                -- Validität
                WHEN CUSTOMER_INDUSTRY NOT LIKE_REGEXPR '[\p{N}]' FLAG 'i'
                    THEN '' --'|Branche keine Zahlen'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 14: CustomerCreditTermsDesc
            -- Validiert Zahlungsbedingungen des Kunden
            -- CUSTOMER_CREDIT_TERMS_DESC
            -- Typen: Vollständigkeit, Einheitlichkeit
            CASE
                -- Vollständigkeit
                WHEN TRIM(CUSTOMER_CREDIT_TERMS_DESC) = '' OR CUSTOMER_CREDIT_TERMS_DESC IS NULL
                    THEN '' --'|ZahlungsZiel leer'
                -- Einheitlichkeit
                WHEN CUSTOMER_CREDIT_TERMS_DESC != TRIM(CUSTOMER_CREDIT_TERMS_DESC)
                    THEN '' --'|ZahlungsZiel mit Leerzeichen'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 15: CustomerPaymentMethod
            -- Validiert Zahlungsmethode aus dem Kunden
            -- CUSTOMER_PAYMENT_METHOD
            -- Typen: Vollständigkeit, Einheitlichkeit
            CASE
                -- Vollständigkeit
                WHEN TRIM(CUSTOMER_PAYMENT_METHOD) = '' OR CUSTOMER_PAYMENT_METHOD IS NULL
                    THEN '' --'|Zahlungsart leer'
                -- Einheitlichkeit
                WHEN CUSTOMER_PAYMENT_METHOD != TRIM(CUSTOMER_PAYMENT_METHOD)
                    THEN '' --'|Zahlungsart mit Leerzeichen'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 16: CustomerPriceGroup
            -- Validiert Preisgruppe des Kunden
            -- CUSTOMER_PRICE_GROUP
            -- Typen: Vollständigkeit, Einheitlichkeit
            CASE
                -- Vollständigkeit
                WHEN TRIM(CUSTOMER_PRICE_GROUP) = '' OR CUSTOMER_PRICE_GROUP IS NULL
                    THEN '' --'|Preisgruppe leer'
                -- Einheitlichkeit
                WHEN CUSTOMER_PRICE_GROUP != TRIM(CUSTOMER_PRICE_GROUP)
                    THEN '' --'|Preisgruppe mit Leerzeichen'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 17: CustomerCreationDate
            -- Validiert Erstellungsdatum des Kunden
            -- CUSTOMER_CREATION_DATE
            -- Typen: Vollständigkeit, Validität, Korrektheit, Aktualität
            CASE
                -- Vollständigkeit
                WHEN CUSTOMER_CREATION_DATE IS NULL
                    THEN '|Anlagedatum leer'
                -- Validität
                WHEN CUSTOMER_CREATION_DATE > CURRENT_DATE
                    THEN '|Anlagedatum in Zukunft'
                -- Aktualität
                WHEN DAYS_BETWEEN(CUSTOMER_CREATION_DATE, CURRENT_DATE) / 365 > 100
                    THEN '|Anlagedatum zu alt'
                -- Korrektheit
                WHEN CUSTOMER_CREATION_DATE < CAST('1900-01-01' AS DATE)
                    THEN '|Anlagedatum vor 1900'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 18: CustomerChangeDate
            -- Validiert Änderungsdatum des Kunden
            -- CUSTOMER_CHANGE_DATE
            -- Typen: Vollständigkeit, Validität, Korrektheit, Konsistenz, Aktualität
            CASE
                -- Vollständigkeit
                WHEN CUSTOMER_CHANGE_DATE IS NULL
                    THEN '|Aenderungsdatum leer'
                -- Validität
                WHEN CUSTOMER_CHANGE_DATE > CURRENT_DATE
                    THEN '|Aenderungsdatum in Zukunft'
                -- Konsistenz
                WHEN CUSTOMER_CHANGE_DATE < CUSTOMER_CREATION_DATE
                    THEN '|Aenderungsdatum vor Anlagedatum'
                -- Aktualität
                WHEN DAYS_BETWEEN(CUSTOMER_CHANGE_DATE, CURRENT_DATE) / 365 > 100
                    THEN '|Aenderungsdatum zu alt'
                -- Korrektheit
                WHEN CUSTOMER_CHANGE_DATE < CAST('1900-01-01' AS DATE)
                    THEN '|Aenderungsdatum vor 1900'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 19: CustomerCreationUser
            -- Validiert Erstellungsbenutzer des Kunden
            -- CUSTOMER_CREATION_USER
            -- Typen: Vollständigkeit, Validität, Genauigkeit, Einheitlichkeit, Zuverlässigkeit
            CASE
                -- Vollständigkeit
                WHEN CUSTOMER_CREATION_DATE IS NOT NULL AND (CUSTOMER_CREATION_USER IS NULL OR TRIM(CUSTOMER_CREATION_USER) = '')
                    THEN '|Anlagebenutzer leer'
                -- Einheitlichkeit
                WHEN CUSTOMER_CREATION_USER != TRIM(CUSTOMER_CREATION_USER)
                    THEN '|Anlagebenutzer mit Leerzeichen'
                -- Genauigkeit
                WHEN CUSTOMER_CREATION_USER IS NOT NULL AND LENGTH(TRIM(CUSTOMER_CREATION_USER)) < 3
                    THEN '' --'|Anlagebenutzer zu kurz'
                -- Validität
                WHEN CUSTOMER_CREATION_USER IS NOT NULL AND CUSTOMER_CREATION_USER NOT LIKE_REGEXPR '^[A-Za-z0-9_.]+$'
                    THEN '' --'|Anlagebenutzer ungültige Zeichen'
                -- Zuverlässigkeit
                WHEN CUSTOMER_CREATION_USER LIKE_REGEXPR '([[:<:]]|^)(test|demo|admin|system|guest|default|invalid)([[:>:]]|$)' FLAG 'i'
                    THEN '' --'|Anlagebenutzer Testkonto'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 20: CustomerChangeUser
            -- Validiert Änderungsbenutzer des Kunden
            -- CUSTOMER_CHANGE_USER
            -- Typen: Vollständigkeit, Validität, Genauigkeit, Einheitlichkeit, Zuverlässigkeit
            CASE
                -- Vollständigkeit
                WHEN CUSTOMER_CHANGE_DATE IS NOT NULL AND (CUSTOMER_CHANGE_USER IS NULL OR TRIM(CUSTOMER_CHANGE_USER) = '')
                    THEN '|Aenderungsbenutzer leer'
                -- Einheitlichkeit
                WHEN CUSTOMER_CHANGE_USER != TRIM(CUSTOMER_CHANGE_USER)
                    THEN '|Aenderungsbenutzer mit Leerzeichen'
                -- Genauigkeit
                WHEN CUSTOMER_CHANGE_USER IS NOT NULL AND LENGTH(TRIM(CUSTOMER_CHANGE_USER)) < 3
                    THEN '' --'|Aenderungsbenutzer zu kurz'
                -- Validität
                WHEN CUSTOMER_CHANGE_USER IS NOT NULL AND CUSTOMER_CHANGE_USER NOT LIKE_REGEXPR '^[A-Za-z0-9_.]+$'
                    THEN '' --'|Aenderungsbenutzer ungültige Zeichen'
                -- Zuverlässigkeit
                WHEN CUSTOMER_CHANGE_USER LIKE_REGEXPR '([[:<:]]|^)(test|demo|guest|default|invalid)([[:>:]]|$)' FLAG 'i'
                    THEN '' --'|Aenderungsbenutzer Testkonto'
                ELSE ''
            END
        ) AS DEFICIENCY_DESCRIPTION
    FROM
        joined j
)

-- ----------------------------------------------------------------------------
-- HAUPTABFRAGE: TOP 25 KUNDEN MIT DEN MEISTEN MÄNGELN
-- Formatiert die Ergebnisse für das DQM-Reporting
-- ----------------------------------------------------------------------------
SELECT
    -- Auskommentieren, wenn alle Kunden ausgegeben werden sollen für Monitoring in Nemo
    -- TOP 25
    '01'                                                                AS RULENUMBER,
    'Kunden-Stammdaten Datenqualitätssicherung'                         AS RULENAME,
    DEFICIENCY_DESCRIPTION                                              AS RULEDESCRIPTION,
    LENGTH(REPLACE_REGEXPR('[^|]' IN DEFICIENCY_DESCRIPTION WITH ''))   AS ERROREVALUATION,
    'S_Kunde'                                                           AS AREA,
    'Kunde'                                                             AS RULEFIELD,
    REPLACE_REGEXPR('\.' IN CUSTOMER_I_D WITH '')                       AS IDENTIFIER,
    REPLACE_REGEXPR(
            '\\s+' IN TRIM(
                COALESCE(ADDRESS_NAME,  '') || ' ' || 
                COALESCE(ADDRESS_NAME2, '') || ' ' || 
                COALESCE(ADDRESS_NAME3, '')
            ) WITH ' '
        )                                                               AS DESCRIPTION,
    REPLACE_REGEXPR(
            '\\s+' IN TRIM(
                MASTER_DATA_SUB_TYPE || 
                '|<Firma>' || COMPANY || 
                '|<Kunde Suchbegriff>' || CUSTOMER_SEARCH_TERM || 
                '|<Kunde Bez 1>' || ADDRESS_NAME || 
                '|<Kunde Bez 2>' || ADDRESS_NAME2 || 
                '|<Kunde Bez 3>' || ADDRESS_NAME3 || 
                '|<Strasse>' || ADDRESS_STREET || 
                '|<Hausnummer>' || ADDRESS_STREET_NO || 
                '|<PLZ>' || ADDRESS_Z_I_P_CODE || 
                '|<Ort>' || ADDRESS_CITY || 
                '|<Bundesland>' || COALESCE(TO_NVARCHAR(ADDRESS_STATE), '') ||
                '|<Land>' || ADDRESS_COUNTRY || 
                '|<Telefon>' || ADDRESS_TELEPHONE || 
                '|<E-Mail>' || ADDRESS_E_MAIL || 
                '|<Adresse Suchbegriff>' || ADDRESS_SEARCH_TERM || 
                '|<URL>' || ADDRESS_U_R_L || 
                '|<Branche>' || CUSTOMER_INDUSTRY || 
                '|<S_ZahlZielSpr.Bezeichnung>' || CUSTOMER_CREDIT_TERMS_DESC || 
                '|<S_Kunde.ZahlungsArt>' || CUSTOMER_PAYMENT_METHOD || 
                '|<S_Kunde.PreisGruppe>' || CUSTOMER_PRICE_GROUP ||
                '|<AnlageDatum>' || COALESCE(TO_NVARCHAR(CUSTOMER_CREATION_DATE), '') ||
                '|<AnlageBenutzer>' || COALESCE(TO_NVARCHAR(CUSTOMER_CREATION_USER), '') ||
                '|<AenderungDatum>' || COALESCE(TO_NVARCHAR(CUSTOMER_CHANGE_DATE), '') ||
                '|<AenderungBenutzer>' || COALESCE(TO_NVARCHAR(CUSTOMER_CHANGE_USER), '')
            ) WITH ' '
        )                                                               AS DESCRIPTION2,
    'Kunde'                                                             AS CATEGORY,
    CURRENT_DATE                                                        AS ANALYSISDATE,
    COMPANY                                                             AS COMPANY,
    'Kunde'                                                             AS FIELDNAME,
    'paSystem'                                                          AS PERSON,
    (CASE
            WHEN DEFICIENCY_DESCRIPTION != '' THEN 'check' ELSE 'ok'
            END
    )                                                                   AS STATUS
FROM
    checks
    -- Auskommentieren, wenn nur die Kunden mit Mängeln ausgegeben werden sollen
    -- WHERE DEFICIENCY_DESCRIPTION <> '' ORDER BY ERROREVALUATION DESC
