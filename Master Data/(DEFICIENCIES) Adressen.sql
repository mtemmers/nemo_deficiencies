-- ================================================================================
-- NEMO DQM Report SQL
-- Report: (DEFICIENCIES) Adressen
-- Internal Name: deficiencies_addresses
-- Generiert am: 2026-07-29T13:58:08+02:00
-- Generator: nemo_deficiencies SQL generator
-- Prüfblöcke: 11
-- Regeln aktiv/inaktiv: 107 / 17
-- DQ-Typen: Vollständigkeit=11, Validität=14, Korrektheit=31, Eindeutigkeit=1, Konsistenz=5, Aktualität=2, Genauigkeit=7, Redundanz=5, Einheitlichkeit=30, Relevanz=5, Zuverlässigkeit=5, Verständlichkeit=8
-- --------------------------------------------------------------------------------
-- Checks:
--   01. ADDRESS_NAME (Name 1-3) (11 aktiv / 1 inaktiv) - Einheitlichkeit, Konsistenz, Redundanz, Relevanz, Validität, Verständlichkeit, Vollständigkeit
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
-- ================================================================================
WITH address_source AS (
    SELECT
        company,					    -- #ERP-Origin: S_Firma.Firma
        MASTER_DATA_SUB_TYPE,           -- #Typ der Stammdaten (z.B. 'CUSTOMER' für Kunden)
        address_i_d,				    -- #ERP-Origin: S_Adresse.AdressNr
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
        address_z_i_p_code			    -- #ERP-Origin: S_Adresse.PLZ
    FROM
        $schema.$table
    WHERE
        UPPER(TRIM(MASTER_DATA_SUB_TYPE)) = 'ADDRESS'
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
            -- Validiert die drei Namensfelder ohne zusammengeführte Hilfsspalte
            -- ADDRESS_NAME
            -- Typen: Vollständigkeit, Validität, Korrektheit, Konsistenz, Redundanz, Einheitlichkeit, Relevanz, Verständlichkeit
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
            -- Validiert Straßenname und länderabhängige Schreibweisen
            -- ADDRESS_STREET
            -- Typen: Vollständigkeit, Validität, Korrektheit, Konsistenz, Aktualität, Genauigkeit, Redundanz, Einheitlichkeit, Relevanz, Verständlichkeit
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
            -- Validiert Hausnummer aus der Stammdatenadresse
            -- ADDRESS_STREET_NO
            -- Typen: Vollständigkeit, Validität, Korrektheit, Genauigkeit, Redundanz, Einheitlichkeit, Relevanz, Verständlichkeit
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
            -- Validiert Suchbegriff aus der Stammdatenadresse
            -- ADDRESS_SEARCH_TERM
            -- Typen: Vollständigkeit, Validität, Einheitlichkeit, Relevanz, Verständlichkeit
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
            -- Validiert Postleitzahl mit länderspezifischen Mustern aus der Stammdatenadresse
            -- ADDRESS_Z_I_P_CODE
            -- Typen: Vollständigkeit, Validität, Korrektheit, Konsistenz, Einheitlichkeit, Zuverlässigkeit
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
            -- Validiert Ortsname aus der Stammdatenadresse
            -- ADDRESS_CITY
            -- Typen: Vollständigkeit, Validität, Einheitlichkeit, Relevanz, Verständlichkeit
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
            -- Validiert Ländercode (ISO 3166-1 alpha-2) aus der Stammdatenadresse
            -- ADDRESS_COUNTRY
            -- Typen: Vollständigkeit, Validität, Einheitlichkeit
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
            -- Validiert Bundesland-Code der Stammdatenadresse
            -- ADDRESS_STATE
            -- Typen: Vollständigkeit, Validität, Konsistenz, Aktualität, Genauigkeit, Einheitlichkeit, Relevanz, Zuverlässigkeit
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
            -- Validiert E-Mail-Adresse aus der Stammdatenadresse
            -- ADDRESS_E_MAIL
            -- Typen: Vollständigkeit, Validität, Korrektheit, Eindeutigkeit, Genauigkeit, Redundanz, Einheitlichkeit, Zuverlässigkeit
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
            -- Validiert Telefonnummer aus der Stammdatenadresse
            -- ADDRESS_TELEPHONE
            -- Typen: Vollständigkeit, Validität, Korrektheit, Konsistenz, Genauigkeit, Redundanz, Einheitlichkeit, Zuverlässigkeit, Verständlichkeit
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
            -- Validiert Website-URL aus der Stammdatenadresse
            -- ADDRESS_U_R_L
            -- Typen: Vollständigkeit, Validität, Korrektheit, Genauigkeit, Einheitlichkeit, Zuverlässigkeit, Verständlichkeit
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
        ) AS DEFICIENCY_DESCRIPTION
    FROM
        address_source j
)

-- ----------------------------------------------------------------------------
-- HAUPTABFRAGE: TOP 25 KUNDEN MIT DEN MEISTEN MÄNGELN
-- Formatiert die Ergebnisse für das DQM-Reporting
-- ----------------------------------------------------------------------------
SELECT
    -- Auskommentieren, wenn alle Kunden ausgegeben werden sollen für Monitoring in Nemo
    -- TOP 25
    '01'                                                                AS RULENUMBER,
    'Adressen-Stammdaten Datenqualitätssicherung'                      AS RULENAME,
    DEFICIENCY_DESCRIPTION                                              AS RULEDESCRIPTION,
    LENGTH(REPLACE_REGEXPR('[^|]' IN DEFICIENCY_DESCRIPTION WITH ''))   AS ERROREVALUATION,
    'S_Adresse'                                                         AS AREA,
    'Adresse'                                                           AS RULEFIELD,
    REPLACE_REGEXPR('\.' IN ADDRESS_I_D WITH '')                        AS IDENTIFIER,
    ADDRESS_NAME                                                        AS DESCRIPTION,
    REPLACE_REGEXPR(
        '\\s+' IN TRIM(
            '|<Typ>' || COALESCE(TO_NVARCHAR(MASTER_DATA_SUB_TYPE), '') ||
            '|<Firma>' || COALESCE(TO_NVARCHAR(COMPANY), '') ||
            '|<Adresse-ID>' || COALESCE(TO_NVARCHAR(ADDRESS_I_D), '') ||
            '|<Adresse Suchbegriff>' || COALESCE(TO_NVARCHAR(ADDRESS_SEARCH_TERM), '') ||
            '|<Name>' || COALESCE(TO_NVARCHAR(ADDRESS_NAME), '') ||
            '|<Name2>' || COALESCE(TO_NVARCHAR(ADDRESS_NAME2), '') ||
            '|<Name3>' || COALESCE(TO_NVARCHAR(ADDRESS_NAME3), '') ||
            '|<Straße>' || COALESCE(TO_NVARCHAR(ADDRESS_STREET), '') ||
            '|<Hausnummer>' || COALESCE(TO_NVARCHAR(ADDRESS_STREET_NO), '') ||
            '|<PLZ>' || COALESCE(TO_NVARCHAR(ADDRESS_Z_I_P_CODE), '') ||
            '|<Ort>' || COALESCE(TO_NVARCHAR(ADDRESS_CITY), '') ||
            '|<Bundesland>' || COALESCE(TO_NVARCHAR(ADDRESS_STATE), '') ||
            '|<Land>' || COALESCE(TO_NVARCHAR(ADDRESS_COUNTRY), '') ||
            '|<Telefon>' || COALESCE(TO_NVARCHAR(ADDRESS_TELEPHONE), '') ||
            '|<E-Mail>' || COALESCE(TO_NVARCHAR(ADDRESS_E_MAIL), '') ||
            '|<URL>' || COALESCE(TO_NVARCHAR(ADDRESS_U_R_L), '')
        ) WITH ' '
    )                                                                    AS DESCRIPTION2,
    'Address'                                                           AS CATEGORY,
    CURRENT_DATE                                                        AS ANALYSISDATE,
    COMPANY                                                             AS COMPANY,
    'Adresse'                                                           AS FIELDNAME,
    'paSystem'                                                          AS PERSON,
    (CASE
            WHEN DEFICIENCY_DESCRIPTION != '' THEN 'check' ELSE 'ok'
            END
    )                                                                   AS STATUS
FROM
    checks
    -- Auskommentieren, wenn nur die Kunden mit Mängeln ausgegeben werden sollen
    -- WHERE DEFICIENCY_DESCRIPTION <> '' ORDER BY ERROREVALUATION DESC
