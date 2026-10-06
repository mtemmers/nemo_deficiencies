-- ================================================================================
-- NEMO DQM Report SQL
-- Report: (DEFICIENCIES) Kontakte
-- Internal Name: deficiencies_contacts
-- Generiert am: 2026-07-29T14:01:53+02:00
-- Generator: nemo_deficiencies SQL generator
-- Prüfblöcke: 23
-- Regeln aktiv/inaktiv: 146 / 98
-- DQ-Typen: Vollständigkeit=23, Validität=48, Korrektheit=40, Eindeutigkeit=1, Konsistenz=10, Aktualität=7, Genauigkeit=17, Redundanz=5, Einheitlichkeit=58, Relevanz=12, Zuverlässigkeit=15, Verständlichkeit=8
-- --------------------------------------------------------------------------------
-- Checks:
--   01. ADDRESS_NAME (1-3) (Kontaktname) (11 aktiv / 1 inaktiv) - Einheitlichkeit, Konsistenz, Redundanz, Relevanz, Validität, Verständlichkeit, Vollständigkeit
--   02. ADDRESS_STREET (Straßenname) (14 aktiv / 0 inaktiv) - Aktualität, Einheitlichkeit, Genauigkeit, Konsistenz, Redundanz, Relevanz, Validität, Verständlichkeit, Vollständigkeit
--   03. ADDRESS_STREET_NO (Hausnummer) (9 aktiv / 1 inaktiv) - Einheitlichkeit, Genauigkeit, Redundanz, Relevanz, Validität, Verständlichkeit, Vollständigkeit
--   04. ADDRESS_Z_I_P_CODE (Postleitzahl) (42 aktiv / 0 inaktiv) - Aktualität, Einheitlichkeit, Konsistenz, Korrektheit, Validität, Vollständigkeit, Zuverlässigkeit
--   05. ADDRESS_CITY (Ort) (7 aktiv / 1 inaktiv) - Einheitlichkeit, Relevanz, Validität, Verständlichkeit, Vollständigkeit
--   06. ADDRESS_COUNTRY (Land) (6 aktiv / 1 inaktiv) - Einheitlichkeit, Validität, Vollständigkeit
--   07. ADDRESS_STATE (Bundesland) (0 aktiv / 8 inaktiv) - Aktualität, Einheitlichkeit, Genauigkeit, Korrektheit, Validität, Vollständigkeit, Zuverlässigkeit
--   08. ADDRESS_E_MAIL (E-Mail) (9 aktiv / 1 inaktiv) - Eindeutigkeit, Einheitlichkeit, Genauigkeit, Korrektheit, Redundanz, Validität, Vollständigkeit, Zuverlässigkeit
--   09. ADDRESS_TELEPHONE (Telefon) (9 aktiv / 1 inaktiv) - Einheitlichkeit, Genauigkeit, Konsistenz, Korrektheit, Redundanz, Validität, Verständlichkeit, Vollständigkeit, Zuverlässigkeit
--   10. ADDRESS_U_R_L (Website) (7 aktiv / 1 inaktiv) - Einheitlichkeit, Genauigkeit, Korrektheit, Validität, Verständlichkeit, Vollständigkeit, Zuverlässigkeit
--   11. ADDRESS_SEARCH_TERM (Suchbegriff - Adresse) (6 aktiv / 2 inaktiv) - Einheitlichkeit, Relevanz, Validität, Verständlichkeit, Vollständigkeit
--   12. CONTACT_CHANGE_DATE (Änderungsdatum) (0 aktiv / 7 inaktiv) - Aktualität, Konsistenz, Korrektheit, Vollständigkeit, Zuverlässigkeit
--   13. CONTACT_CHANGE_USER (Änderungsbenutzer) (0 aktiv / 7 inaktiv) - Aktualität, Einheitlichkeit, Genauigkeit, Korrektheit, Validität
--   14. CONTACT_CREATION_DATE (Erstellungsdatum) (0 aktiv / 7 inaktiv) - Aktualität, Konsistenz, Korrektheit, Vollständigkeit, Zuverlässigkeit
--   15. CONTACT_CREATION_USER (Erstellungsbenutzer) (0 aktiv / 7 inaktiv) - Aktualität, Einheitlichkeit, Genauigkeit, Korrektheit, Validität
--   16. CONTACT_CREDIT_TERMS_DESC (Zahlungsbedingungen) (0 aktiv / 4 inaktiv) - Einheitlichkeit, Genauigkeit, Relevanz, Validität
--   17. CONTACT_INDUSTRY (Branche) (0 aktiv / 7 inaktiv) - Einheitlichkeit, Genauigkeit, Relevanz, Validität, Zuverlässigkeit
--   18. CONTACT_NAME (Kontaktname) (0 aktiv / 10 inaktiv) - Einheitlichkeit, Genauigkeit, Korrektheit, Relevanz, Validität, Zuverlässigkeit
--   19. CONTACT_PRICE_GROUP (Preisgruppe) (0 aktiv / 7 inaktiv) - Einheitlichkeit, Genauigkeit, Validität, Zuverlässigkeit
--   20. CONTACT_SEARCH_TERM (Suchbegriff Kontakt) (0 aktiv / 9 inaktiv) - Einheitlichkeit, Genauigkeit, Relevanz, Validität
--   21. CONTACT_SELECTION (Selektion) (0 aktiv / 7 inaktiv) - Einheitlichkeit, Genauigkeit, Relevanz, Validität
--   22. CONTACT_SPECIALIST (Sachbearbeiter) (0 aktiv / 8 inaktiv) - Einheitlichkeit, Genauigkeit, Korrektheit, Validität, Zuverlässigkeit
--   23. CONTACT_MASTER_FIELDS (weitere Kontaktfelder) (26 aktiv / 1 inaktiv) - Einheitlichkeit, Konsistenz, Validität, Vollständigkeit
-- ================================================================================
WITH customer_contact_source AS (
    SELECT
        company,
        MASTER_DATA_SUB_TYPE,
		contact_i_d,					-- #ERP-Origin: VC_Interessent.Interessent
		address_i_d,					-- #ERP-Origin: S_Adresse.AdressNr
		contact_customer_i_d,			-- #ERP-Origin: VC_Interessent.Kunde
		contact_adress_no,				-- #ERP-Origin: VC_Interessent.AdressNr
		contact_association,			-- #ERP-Origin: VC_Interessent.Verband
		contact_change_date,			-- #ERP-Origin: VC_Interessent.AenderungDatum
		contact_change_user,			-- #ERP-Origin: VC_Interessent.AenderungBenutzer
		contact_company_group,			-- #ERP-Origin: VC_Interessent.Konzern
		contact_creation_date,			-- #ERP-Origin: VC_Interessent.AnlageDatum
		contact_creation_user,			-- #ERP-Origin: VC_Interessent.AnlageBenutzer
		contact_credit_terms,			-- #ERP-Origin: VC_Interessent.ZahlungsZiel
		contact_credit_terms_desc,		-- #ERP-Origin: S_ZahlZielSpr.Bezeichnung
		contact_discount_group,			-- #ERP-Origin: VC_Interessent.Rabattgruppe
		contact_discount_visible,		-- #ERP-Origin: VC_Interessent.RabattArt
		contact_industry,				-- #ERP-Origin: VC_Interessent.Branche
		contact_language,				-- #ERP-Origin: VC_Interessent.Sprache
		contact_name,					-- #ERP-Origin: S_Adresse.Name1
		contact_o_i_d,					-- #ERP-Origin: VC_Interessent.VC_Interessent_Obj
		contact_payment_method,			-- #ERP-Origin: VC_Interessent.ZahlungsArt
		contact_payment_method_desc,	-- #ERP-Origin: ACM SB_PaymentMethods_desc
		contact_price_group,			-- #ERP-Origin: VC_Interessent.PreisGruppe
		contact_search_term,			-- #ERP-Origin: VC_Interessent.Suchbegriff
		contact_selection,				-- #ERP-Origin: VC_Interessent.Selektion
		contact_shipping_type,			-- #ERP-Origin: VC_Interessent.VersandArt
		contact_shipping_type_desc,		-- #ERP-Origin: S_VersandArtSpr.Bezeichnung
		contact_specialist,				-- #ERP-Origin: VC_Interessent.Sachbearbeiter
		contact_work_group,				-- #ERP-Origin: VC_Interessent.VerteilerGruppe
		contact_z_i_p,					-- #ERP-Origin: VC_Interessent.PLZ
		address_box,					-- #ERP-Origin: S_Adresse.Postfach
		address_city,					-- #ERP-Origin: S_Adresse.Ort
		address_country,				-- #ERP-Origin: S_Adresse.Staat
		address_e_mail,					-- #ERP-Origin: S_Adresse.EMail
		address_first_name,				-- #ERP-Origin: S_Adresse.Vorname
		address_name,					-- #ERP-Origin: S_Adresse.Name1
		address_name2,					-- #ERP-Origin: S_Adresse.Name2
		address_name3,					-- #ERP-Origin: S_Adresse.Name3
		address_o_i_d,					-- #ERP-Origin: S_Adresse.S_Adresse_Obj
		address_search_term,			-- #ERP-Origin: S_Adresse.Suchbegriff
		address_state,					-- #ERP-Origin: S_Adresse.Bundesland
		address_street,					-- #ERP-Origin: S_Adresse.Strasse
		address_street_no,				-- #ERP-Origin: S_Adresse.Hausnummer
		address_telephone,				-- #ERP-Origin: S_Adresse.Telefon
		address_u_r_l,					-- #ERP-Origin: S_Adresse.HomePage
		address_z_i_p_box,				-- #ERP-Origin: S_Adresse.PLZ_Postfach
		address_z_i_p_code				-- #ERP-Origin: S_Adresse.PLZ
    FROM
        $schema.$table
    WHERE
        TRIM(UPPER(MASTER_DATA_SUB_TYPE)) = 'CONTACT'
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
        customer_contact_source c
        INNER JOIN process_source p ON c.COMPANY = p.COMPANY
        AND p.CUSTOMER_I_D = c.contact_customer_i_d
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
            -- Validiert die kombinierten Namensfelder
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
            -- Validiert Straßenname aus den Kontakten
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
            -- Validiert Hausnummer aus den Kontakten
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
            -- PRÜFUNG 4: AddressZIPCode
            -- Validiert Postleitzahl mit länderspezifischen Mustern
            -- Typen: Aktualität, Einheitlichkeit, Konsistenz, Korrektheit, Validität, Vollständigkeit, Zuverlässigkeit
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
                -- Vollständigkeit
                WHEN TRIM(CONTACT_Z_I_P) = '' OR CONTACT_Z_I_P IS NULL
                    THEN '|PLZ (Kontakte) leer'
                -- Vollständigkeit
                WHEN CONTACT_Z_I_P != TRIM(CONTACT_Z_I_P)
                    THEN '|PLZ (Kontakte) mit Leerzeichen'
                -- Korrektheit
                WHEN CONTACT_Z_I_P NOT LIKE_REGEXPR '[\p{N}]'
                    THEN '|PLZ (Kontakte) keine Zahlen'
                -- Einheitlichkeit
                WHEN ADDRESS_COUNTRY = 'NL' AND TRIM(CONTACT_Z_I_P) <> '' AND CONTACT_Z_I_P NOT LIKE_REGEXPR '^[\p{N}]{4}[\s]?[A-Za-z]{2}$'
                    THEN '|PLZ (Kontakte) Muster <> NL'
                -- Einheitlichkeit
                WHEN ADDRESS_COUNTRY = 'PL' AND TRIM(CONTACT_Z_I_P) <> '' AND CONTACT_Z_I_P NOT LIKE_REGEXPR '^[\p{N}]{2}-?[\p{N}]{3}$'
                    THEN '|PLZ (Kontakte) Muster <> PL'
                -- Einheitlichkeit
                WHEN ADDRESS_COUNTRY = 'PT' AND TRIM(CONTACT_Z_I_P) <> '' AND CONTACT_Z_I_P NOT LIKE_REGEXPR '^[\p{N}]{4}-?[\p{N}]{3}$'
                    THEN '|PLZ (Kontakte) Muster <> PT'
                -- Einheitlichkeit
                WHEN ADDRESS_COUNTRY IN ('D', 'DE', 'ES', 'FR', 'IT', 'US', 'MX', 'MA', 'DZ', 'EG', 'GR', 'TR', 'UA', 'TH', 'MY', 'PH', 'PE', 'JO', 'SA', 'TN', 'MK', 'GT', 'HN', 'NI', 'SV', 'CR', 'PA', 'VE', 'GE', 'LT', 'LV') AND TRIM(CONTACT_Z_I_P) <> '' AND CONTACT_Z_I_P NOT LIKE_REGEXPR '^[\p{N}]{5}$'
                    THEN '|PLZ (Kontakte) 5 Zahlen erwartet'
                -- Einheitlichkeit
                WHEN ADDRESS_COUNTRY IN ('AT', 'CH', 'DK', 'NO', 'SE', 'BE', 'LU', 'LI', 'IS', 'AU', 'BA', 'ME', 'MM', 'KH', 'LA', 'NP') AND TRIM(CONTACT_Z_I_P) <> '' AND CONTACT_Z_I_P NOT LIKE_REGEXPR '^[\p{N}]{4}$'
                    THEN '|PLZ (Kontakte) 4 Zahlen erwartet'
                -- Einheitlichkeit
                WHEN ADDRESS_COUNTRY IN ('RU', 'CN', 'IN', 'KZ', 'KG', 'UZ', 'TJ', 'TM', 'VN', 'BY', 'SG', 'CO', 'CL') AND TRIM(CONTACT_Z_I_P) <> '' AND CONTACT_Z_I_P NOT LIKE_REGEXPR '^[\p{N}]{6}$'
                    THEN '|PLZ (Kontakte) 6 Zahlen erwartet'
                -- Einheitlichkeit
                WHEN ADDRESS_COUNTRY IN ('IR') AND TRIM(CONTACT_Z_I_P) <> '' AND CONTACT_Z_I_P NOT LIKE_REGEXPR '^[\p{N}]{7}$'
                    THEN '|PLZ (Kontakte) 7 Zahlen erwartet'
                -- Einheitlichkeit
                WHEN ADDRESS_COUNTRY IN ('IS') AND TRIM(CONTACT_Z_I_P) <> '' AND CONTACT_Z_I_P NOT LIKE_REGEXPR '^[\p{N}]{3}$'
                    THEN '|PLZ (Kontakte) 3 Zahlen erwartet'
                -- Aktualität
                WHEN CONTACT_Z_I_P LIKE_REGEXPR '(00000|99999)'
                    THEN '|PLZ (Kontakte) Testwert'
                -- Einheitlichkeit
                WHEN ADDRESS_Z_I_P_CODE != CONTACT_Z_I_P AND TRIM(ADDRESS_Z_I_P_CODE) <> '' AND TRIM(CONTACT_Z_I_P) <> ''
                    THEN '|PLZ-Inkonsistenz: PLZ (Adresse) <> CONTACT_Z_I_P'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 5: AddressCity
            -- Validiert Ortsname
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
            -- PRÜFUNG 6: AddressCountry
            -- Validiert Ländercode (ISO 3166-1 alpha-2)
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
            -- PRÜFUNG 7: AddressState
            -- Validiert Bundesland-Code
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
            -- PRÜFUNG 8: AddressEMail
            -- Validiert E-Mail-Adresse
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
            -- PRÜFUNG 9: AddressTelephone
            -- Validiert Telefonnummer
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
            -- PRÜFUNG 10: AddressURL
            -- Validiert Website-URL
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
            -- PRÜFUNG 11: AddressSearchTerm
            -- Validiert Adress-Suchbegriff
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
            -- PRÜFUNG 12: ContactChangeDate
            -- Validiert Änderungsdatum mit mehreren Datenqualitätsregeln
            -- Typen: Aktualität, Konsistenz, Korrektheit, Vollständigkeit, Zuverlässigkeit
            CASE
                -- Vollständigkeit
                WHEN contact_change_date IS NULL
                    THEN '' --'|Änderungsdatum leer'
                -- Korrektheit
                WHEN contact_change_date > CURRENT_DATE
                    THEN '' --'|Änderungsdatum in der Zukunft'
                -- Konsistenz
                WHEN contact_change_date < contact_creation_date
                    THEN '' --'|Änderungsdatum vor Erstellungsdatum'
                -- Aktualität
                WHEN DAYS_BETWEEN(contact_change_date, CURRENT_DATE) > 3650
                    THEN '' --'|Änderungsdatum älter als 10 Jahre'
                -- Vollständigkeit
                WHEN DAYS_BETWEEN(contact_change_date, CURRENT_DATE) = 0 AND contact_change_user IS NULL
                    THEN '' --'|Heute geändert, aber keine Änderungsuser'
                -- Zuverlässigkeit
                WHEN YEAR(contact_change_date) < 2000
                    THEN '' --'|Änderungsdatum vor Jahr 2000 (Testwert?)'
                -- Konsistenz
                WHEN contact_change_date = contact_creation_date AND contact_change_user != contact_creation_user
                    THEN '' --'|Änderungs- und Erstellungsdatum gleich, aber unterschiedliche Benutzer'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 13: ContactChangeUser
            -- Validiert Änderungsbenutzer mit mehreren Datenqualitätsregeln
            -- Typen: Aktualität, Einheitlichkeit, Genauigkeit, Korrektheit, Validität
            CASE
                -- Einheitlichkeit
                WHEN TRIM(contact_change_user) = '' OR contact_change_user IS NULL
                    THEN '' --'|Änderungsbenutzer leer'
                -- Validität
                WHEN contact_change_user != TRIM(contact_change_user)
                    THEN '' --'|Änderungsbenutzer mit Leerzeichen'
                -- Genauigkeit
                WHEN LENGTH(contact_change_user) > 255
                    THEN '' --'|Änderungsbenutzer zu lang (>255 Zeichen)'
                -- Validität
                WHEN contact_change_user NOT LIKE_REGEXPR '^[\p{L}\p{N}._\-@]+$' FLAG 'i'
                    THEN '' --'|Änderungsbenutzer ungültig (Sonderzeichen)'
                -- Einheitlichkeit
                WHEN contact_change_date IS NOT NULL AND (contact_change_user IS NULL OR TRIM(contact_change_user) = '')
                    THEN '' --'|Änderungsdatum vorhanden, aber kein Änderungsbenutzer'
                -- Korrektheit
                WHEN contact_change_date > CURRENT_DATE AND contact_change_user IS NOT NULL
                    THEN '' --'|Änderungsbenutzer bei Zukunftsdatum'
                -- Aktualität
                WHEN contact_change_user LIKE_REGEXPR '([[:<:]]|^)(test|demo|admin|system|noreply|no-reply|null|undefined|unknown|administrator|guest|anonymous|invalid|obsolete|deprecated|inactive|disabled|deleted|archived|suspended|blocked|locked|temp|temporary|test_|_test|tmp_|_tmp)([[:>:]]|$)' FLAG 'i'
                    THEN '' --'|Änderungsbenutzer verdächtig (Test/System-Account)'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 14: ContactCreationDate
            -- Validiert Erstellungsdatum mit mehreren Datenqualitätsregeln
            -- Typen: Aktualität, Konsistenz, Korrektheit, Vollständigkeit, Zuverlässigkeit
            CASE
                -- Vollständigkeit
                WHEN contact_creation_date IS NULL
                    THEN '' --'|Erstellungsdatum leer'
                -- Korrektheit
                WHEN contact_creation_date > CURRENT_DATE
                    THEN '' --'|Erstellungsdatum in der Zukunft'
                -- Korrektheit
                WHEN contact_creation_date > contact_change_date
                    THEN '' --'|Erstellungsdatum nach Änderungsdatum'
                -- Aktualität
                WHEN DAYS_BETWEEN(contact_creation_date, CURRENT_DATE) > 14600
                    THEN '' --'|Erstellungsdatum älter als 40 Jahre'
                -- Zuverlässigkeit
                WHEN YEAR(contact_creation_date) < 2000
                    THEN '' --'|Erstellungsdatum vor Jahr 2000 (Testwert?)'
                -- Korrektheit
                WHEN DAYS_BETWEEN(contact_creation_date, CURRENT_DATE) > 7300 AND DAYS_BETWEEN(contact_change_date, CURRENT_DATE) > 7300
                    THEN '' --'|Datensatz seit >20 Jahren nicht verändert'
                -- Konsistenz
                WHEN contact_creation_date = contact_change_date AND contact_creation_user != contact_change_user
                    THEN '' --'|Erstellungs- und Änderungsdatum gleich, aber unterschiedliche Benutzer'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 15: ContactCreationUser
            -- Validiert Erstellungsbenutzer mit mehreren Datenqualitätsregeln
            -- Typen: Aktualität, Einheitlichkeit, Genauigkeit, Korrektheit, Validität
            CASE
                -- Einheitlichkeit
                WHEN TRIM(contact_creation_user) = '' OR contact_creation_user IS NULL
                    THEN '' --'|Erstellungsbenutzer leer'
                -- Validität
                WHEN contact_creation_user != TRIM(contact_creation_user)
                    THEN '' --'|Erstellungsbenutzer mit Leerzeichen'
                -- Genauigkeit
                WHEN LENGTH(contact_creation_user) > 255
                    THEN '' --'|Erstellungsbenutzer zu lang (>255 Zeichen)'
                -- Validität
                WHEN contact_creation_user NOT LIKE_REGEXPR '^[\p{L}\p{N}._\-@]+$' FLAG 'i'
                    THEN '' --'|Erstellungsbenutzer ungültig (Sonderzeichen)'
                -- Einheitlichkeit
                WHEN contact_creation_date IS NOT NULL AND (contact_creation_user IS NULL OR TRIM(contact_creation_user) = '')
                    THEN '' --'|Erstellungsdatum vorhanden, aber kein Erstellungsbenutzer'
                -- Korrektheit
                WHEN contact_creation_date > CURRENT_DATE AND contact_creation_user IS NOT NULL
                    THEN '' --'|Erstellungsbenutzer bei Zukunftsdatum'
                -- Aktualität
                WHEN contact_creation_user LIKE_REGEXPR '([[:<:]]|^)(test|demo|admin|system|noreply|no-reply|null|undefined|unknown|administrator|guest|anonymous|invalid|obsolete|deprecated|inactive|disabled|deleted|archived|suspended|blocked|locked|temp|temporary|test_|_test|tmp_|_tmp|import|migration|batch|script|automation)([[:>:]]|$)' FLAG 'i'
                    THEN '' --'|Erstellungsbenutzer verdächtig (Test/System-Account)'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 16: ContactCreditTermsDesc
            -- Validiert Zahlungsbedingungen mit mehreren Datenqualitätsregeln
            -- Typen: Einheitlichkeit, Genauigkeit, Relevanz, Validität
            CASE
                -- Einheitlichkeit
                WHEN TRIM(contact_credit_terms_desc) = '' OR contact_credit_terms_desc IS NULL
                    THEN '' --'|Zahlungsbedingungen leer'
                -- Validität
                WHEN contact_credit_terms_desc != TRIM(contact_credit_terms_desc)
                    THEN '' --'|Zahlungsbedingungen mit führendem/abschließendem Leerzeichen'
                -- Genauigkeit
                WHEN LENGTH(contact_credit_terms_desc) > 500
                    THEN '' --'|Zahlungsbedingungen zu lang (>500 Zeichen)'
                -- Relevanz
                WHEN contact_credit_terms_desc LIKE_REGEXPR 'Bitte Text' FLAG 'i'
                    THEN '' --'|Zahlungsbedingungen: Platzhalter nicht ausgefüllt'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 17: ContactIndustry
            -- Validiert Branchenkode (2-3 Ziffern oder 1 Buchstabe)
            -- Typen: Einheitlichkeit, Genauigkeit, Relevanz, Validität, Zuverlässigkeit
            CASE
                -- Einheitlichkeit
                WHEN TRIM(contact_industry) = '' OR contact_industry IS NULL
                    THEN '' --'|Branche leer'
                -- Validität
                WHEN contact_industry != TRIM(contact_industry)
                    THEN '' --'|Branche mit Leerzeichen'
                -- Genauigkeit
                WHEN LENGTH(contact_industry) > 10
                    THEN '' --'|Branche zu lang (>10 Zeichen)'
                -- Validität
                WHEN NOT (contact_industry LIKE_REGEXPR '^[0-9]{2,3}$' OR contact_industry LIKE_REGEXPR '^[A-Z]$' FLAG 'i')
                    THEN '' --'|Branche ungültig (nicht 2-3 Ziffern oder 1 Buchstabe)'
                -- Zuverlässigkeit
                WHEN contact_industry LIKE_REGEXPR '^0{2,3}$'
                    THEN '' --'|Branche Nur Nullen (Testwert?)'
                -- Zuverlässigkeit
                WHEN contact_industry LIKE_REGEXPR '^9{2,3}$'
                    THEN '' --'|Branche Nur Neunen (Testwert?)'
                -- Relevanz
                WHEN contact_industry LIKE_REGEXPR '([[:<:]]|^)(test|demo|unknown|undefined|n\.?a\.?|xxx|temp)([[:>:]]|$)' FLAG 'i'
                    THEN '' --'|Branche verdächtig (Test/Platzhalter)'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 18: ContactName
            -- Validiert Kontaktname mit diakritischen Zeichen und Sonderzeichenerkennung
            -- Typen: Einheitlichkeit, Genauigkeit, Korrektheit, Relevanz, Validität, Zuverlässigkeit
            CASE
                -- Einheitlichkeit
                WHEN TRIM(contact_name) = '' OR contact_name IS NULL
                    THEN '' --'|Kontaktname leer'
                -- Validität
                WHEN contact_name != TRIM(contact_name)
                    THEN '' --'|Kontaktname mit führendem/abschließendem Leerzeichen'
                -- Genauigkeit
                WHEN LENGTH(contact_name) > 255
                    THEN '' --'|Kontaktname zu lang (>255 Zeichen)'
                -- Validität
                WHEN contact_name NOT LIKE_REGEXPR '[\p{L}]' FLAG 'i'
                    THEN '' --'|Kontaktname keine Buchstaben'
                -- Validität
                WHEN contact_name LIKE_REGEXPR ' +'
                    THEN '' --'|Kontaktname mit mehreren Leerzeichen hintereinander'
                -- Zuverlässigkeit
                WHEN contact_name LIKE_REGEXPR '[\#\$\%\&\*\^\~\`\|\\<>\{\}\[\]]+'
                    THEN '' --'|Kontaktname mit verdächtigen Sonderzeichen'
                -- Korrektheit
                WHEN contact_name LIKE_REGEXPR '^[0-9]+$'
                    THEN '' --'|Kontaktname nur Zahlen'
                -- Relevanz
                WHEN contact_name LIKE_REGEXPR '([[:<:]]|^)(test|demo|unknown|undefined|n\.?a\.?|xxx|temp|temp|test_|_test|invalid|obsolete|deprecated)([[:>:]]|$)' FLAG 'i'
                    THEN '' --'|Kontaktname verdächtig (Test/Platzhalter)'
                -- Relevanz
                WHEN contact_name LIKE_REGEXPR '([[:<:]]|^)(bitte|please|ändern|change|edit|tbd|todo|wip|work in progress)([[:>:]]|$)' FLAG 'i'
                    THEN '' --'|Kontaktname: Platzhalter/Anweisung'
                -- Validität
                WHEN contact_name NOT LIKE_REGEXPR '^[\p{L}\p{N}\s\-\.,''&/:()]+$' FLAG 'i'
                    THEN '' --'|Kontaktname enthält unerlaubte Zeichen'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 19: ContactPriceGroup
            -- Validiert Preisgruppe (exakt 3 Ziffern)
            -- Typen: Einheitlichkeit, Genauigkeit, Validität, Zuverlässigkeit
            CASE
                -- Einheitlichkeit
                WHEN TRIM(contact_price_group) = '' OR contact_price_group IS NULL
                    THEN '' --'|Preisgruppe leer'
                -- Validität
                WHEN contact_price_group != TRIM(contact_price_group)
                    THEN '' --'|Preisgruppe mit Leerzeichen'
                -- Genauigkeit
                WHEN LENGTH(TRIM(contact_price_group)) <> 3
                    THEN '' --'|Preisgruppe nicht exakt 3 Zeichen'
                -- Validität
                WHEN contact_price_group NOT LIKE_REGEXPR '^[0-9]{3}$'
                    THEN '' --'|Preisgruppe ungültig (nicht 3 Ziffern)'
                -- Zuverlässigkeit
                WHEN contact_price_group = '000'
                    THEN '' --'|Preisgruppe: 000 (Testwert?)'
                -- Zuverlässigkeit
                WHEN contact_price_group = '999'
                    THEN '' --'|Preisgruppe: 999 (Testwert?)'
                -- Zuverlässigkeit
                WHEN contact_price_group LIKE_REGEXPR '111|222|333|444|555|666|777|888'
                    THEN '' --'|Preisgruppe: Nur gleiche Ziffern (verdächtig)'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 20: ContactSearchTerm
            -- Validiert Suchbegriff (ohne diakritische/Sonderzeichen)
            -- Typen: Einheitlichkeit, Genauigkeit, Relevanz, Validität
            CASE
                -- Einheitlichkeit
                WHEN TRIM(contact_search_term) = '' OR contact_search_term IS NULL
                    THEN '' --'|Suchbegriff leer'
                -- Validität
                WHEN contact_search_term != TRIM(contact_search_term)
                    THEN '' --'|Suchbegriff mit führendem/abschließendem Leerzeichen'
                -- Genauigkeit
                WHEN LENGTH(contact_search_term) > 255
                    THEN '' --'|Suchbegriff zu lang (>255 Zeichen)'
                -- Genauigkeit
                WHEN LENGTH(TRIM(contact_search_term)) < 2
                    THEN '' --'|Suchbegriff zu kurz (<2 Zeichen)'
                -- Validität
                WHEN contact_search_term LIKE_REGEXPR ' +'
                    THEN '' --'|Suchbegriff mit mehreren Leerzeichen hintereinander'
                -- Validität
                WHEN contact_search_term NOT LIKE_REGEXPR '^[A-Za-z0-9\s\-]+$'
                    THEN '' --'|Suchbegriff enthält unerlaubte Zeichen (nur A-Z, 0-9, Leerzeichen, Bindestrich erlaubt)'
                -- Validität
                WHEN contact_search_term LIKE_REGEXPR '^[0-9\s\-]+$'
                    THEN '' --'|Suchbegriff nur Zahlen/Leerzeichen (keine Buchstaben)'
                -- Relevanz
                WHEN contact_search_term LIKE_REGEXPR '([[:<:]]|^)(test|demo|unknown|undefined|n\.?a\.?|xxx|temp|invalid|sample|beispiel|muster)([[:>:]]|$)' FLAG 'i'
                    THEN '' --'|Suchbegriff verdächtig (Test/Platzhalter)'
                -- Relevanz
                WHEN contact_search_term LIKE_REGEXPR '([[:<:]]|^)(bitte|please|ändern|change|edit|tbd|todo|wip)([[:>:]]|$)' FLAG 'i'
                    THEN '' --'|Suchbegriff: Anweisung statt Begriff'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 21: ContactSelection
            -- Validiert Auswahl/Selektion mit Konsistenzprüfung zu contact_city
            -- Typen: Einheitlichkeit, Genauigkeit, Relevanz, Validität
            CASE
                -- Einheitlichkeit
                WHEN TRIM(contact_selection) = '' OR contact_selection IS NULL
                    THEN '' --'|Selektion leer'
                -- Validität
                WHEN contact_selection != TRIM(contact_selection)
                    THEN '' --'|Selektion mit führendem/abschließendem Leerzeichen'
                -- Genauigkeit
                WHEN LENGTH(contact_selection) > 255
                    THEN '' --'|Selektion zu lang (>255 Zeichen)'
                -- Validität
                WHEN contact_selection LIKE_REGEXPR '\s+'
                    THEN '' --'|Selektion mit mehreren Leerzeichen hintereinander'
                -- Validität
                WHEN contact_selection NOT LIKE_REGEXPR '^[\p{L}\p{N}\s\-\.,''&/:()]+$' FLAG 'i'
                    THEN '' --'|Selektion enthält unerlaubte Zeichen'
                -- Relevanz
                WHEN contact_selection LIKE_REGEXPR '([[:<:]]|^)(test|demo|unknown|undefined|n\.?a\.?|xxx|temp|invalid|muster)([[:>:]]|$)' FLAG 'i'
                    THEN '' --'|Selektion verdächtig (Test/Platzhalter)'
                -- Einheitlichkeit
                WHEN UPPER(contact_selection) = UPPER(ADDRESS_CITY) AND contact_selection != ADDRESS_CITY
                    THEN '' --'|Selektion und Ort unterscheiden sich nur in Groß-/Kleinschreibung'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 22: ContactSpecialist
            -- Validiert Sachbearbeiter-Code
            -- Typen: Einheitlichkeit, Genauigkeit, Korrektheit, Validität, Zuverlässigkeit
            CASE
                -- Einheitlichkeit
                WHEN TRIM(contact_specialist) = '' OR contact_specialist IS NULL
                    THEN '' --'|Sachbearbeiter-Code leer'
                -- Validität
                WHEN contact_specialist != TRIM(contact_specialist)
                    THEN '' --'|Sachbearbeiter-Code mit Leerzeichen'
                -- Genauigkeit
                WHEN LENGTH(TRIM(contact_specialist)) <> 3
                    THEN '' --'|Sachbearbeiter-Code nicht exakt 3 Zeichen'
                -- Validität
                WHEN contact_specialist NOT LIKE_REGEXPR '^[A-Z]{3}$'
                    THEN '' --'|Sachbearbeiter-Code ungültig (nicht 3 Großbuchstaben)'
                -- Validität
                WHEN contact_specialist != UPPER(contact_specialist)
                    THEN '' --'|Sachbearbeiter-Code enthält Kleinbuchstaben oder Leerzeichen'
                -- Zuverlässigkeit
                WHEN contact_specialist LIKE_REGEXPR '^[AAA|EEE|III|OOO|UUU|ZZZ]+$'
                    THEN '' --'|Sachbearbeiter-Code: Nur gleiche Buchstaben (verdächtig)'
                -- Zuverlässigkeit
                WHEN contact_specialist LIKE_REGEXPR '([[:<:]]|^)(TST|DEM|XXX|TMP|DEL|INV|TEST|ADMIN)([[:>:]]|$)' FLAG 'i'
                    THEN '' --'|Sachbearbeiter-Code verdächtig (Test/System-Code)'
                -- Korrektheit
                WHEN contact_specialist LIKE_REGEXPR '^[^A-Z]'
                    THEN '' --'|Sachbearbeiter-Code beginnt nicht mit Buchstaben'
                ELSE ''
            END
            ||
            -- ================================================================
            -- PRÜFUNG 23: ContactID
            -- Ergänzt Prüfungen für bislang nicht berücksichtigte contact_ Felder
            -- Typen: Vollständigkeit, Validität, Konsistenz, Einheitlichkeit
            CASE
                -- Vollständigkeit
                WHEN CONTACT_I_D IS NULL OR TRIM(TO_NVARCHAR(CONTACT_I_D)) = ''
                    THEN '|Kontakt-ID leer'
                -- Validität
                WHEN TO_NVARCHAR(CONTACT_I_D) NOT LIKE_REGEXPR '^[A-Za-z0-9._-]+$'
                    THEN '|Kontakt-ID ungültiges Format'
                -- Vollständigkeit
                WHEN CONTACT_CUSTOMER_I_D IS NULL OR TRIM(TO_NVARCHAR(CONTACT_CUSTOMER_I_D)) = ''
                    THEN '|Kontakt-Kunden-ID leer'
                -- Validität
                WHEN TO_NVARCHAR(CONTACT_CUSTOMER_I_D) NOT LIKE_REGEXPR '^[A-Za-z0-9._-]+$'
                    THEN '|Kontakt-Kunden-ID ungültiges Format'
                -- Vollständigkeit
                WHEN CONTACT_ADRESS_NO IS NULL OR TRIM(TO_NVARCHAR(CONTACT_ADRESS_NO)) = ''
                    THEN '|Kontakt-Adressnummer leer'
                -- Validität
                WHEN TO_NVARCHAR(CONTACT_ADRESS_NO) NOT LIKE_REGEXPR '^[A-Za-z0-9._-]+$'
                    THEN '|Kontakt-Adressnummer ungültiges Format'
                -- Einheitlichkeit
                WHEN TO_NVARCHAR(CONTACT_ASSOCIATION) <> TRIM(TO_NVARCHAR(CONTACT_ASSOCIATION)) OR TO_NVARCHAR(CONTACT_COMPANY_GROUP) <> TRIM(TO_NVARCHAR(CONTACT_COMPANY_GROUP))
                    THEN '|Verband oder Konzern mit Rand-Leerzeichen'
                -- Validität
                WHEN COALESCE(TO_NVARCHAR(CONTACT_ASSOCIATION), '') <> '' AND TO_NVARCHAR(CONTACT_ASSOCIATION) NOT LIKE_REGEXPR '^[\p{L}\p{N}\s._&/()-]+$' FLAG 'i'
                    THEN '|Verband ungültige Zeichen'
                -- Validität
                WHEN COALESCE(TO_NVARCHAR(CONTACT_COMPANY_GROUP), '') <> '' AND TO_NVARCHAR(CONTACT_COMPANY_GROUP) NOT LIKE_REGEXPR '^[\p{L}\p{N}\s._&/()-]+$' FLAG 'i'
                    THEN '|Konzern ungültige Zeichen'
                -- Einheitlichkeit
                WHEN TO_NVARCHAR(CONTACT_CREDIT_TERMS) <> TRIM(TO_NVARCHAR(CONTACT_CREDIT_TERMS))
                    THEN '|Zahlungsziel-Code mit Rand-Leerzeichen'
                -- Validität
                WHEN COALESCE(TO_NVARCHAR(CONTACT_CREDIT_TERMS), '') <> '' AND TO_NVARCHAR(CONTACT_CREDIT_TERMS) NOT LIKE_REGEXPR '^[A-Za-z0-9._-]+$'
                    THEN '|Zahlungsziel-Code ungültiges Format'
                -- Einheitlichkeit
                WHEN TO_NVARCHAR(CONTACT_DISCOUNT_GROUP) <> TRIM(TO_NVARCHAR(CONTACT_DISCOUNT_GROUP)) OR TO_NVARCHAR(CONTACT_DISCOUNT_VISIBLE) <> TRIM(TO_NVARCHAR(CONTACT_DISCOUNT_VISIBLE))
                    THEN '|Rabattgruppe oder Rabattart mit Rand-Leerzeichen'
                -- Validität
                WHEN COALESCE(TO_NVARCHAR(CONTACT_DISCOUNT_GROUP), '') <> '' AND TO_NVARCHAR(CONTACT_DISCOUNT_GROUP) NOT LIKE_REGEXPR '^[A-Za-z0-9._-]+$'
                    THEN '|Rabattgruppe ungültiges Format'
                -- Validität
                WHEN COALESCE(TO_NVARCHAR(CONTACT_DISCOUNT_VISIBLE), '') <> '' AND TO_NVARCHAR(CONTACT_DISCOUNT_VISIBLE) NOT LIKE_REGEXPR '^[A-Za-z0-9._-]+$'
                    THEN '|Rabattart ungültiges Format'
                -- Vollständigkeit
                WHEN CONTACT_LANGUAGE IS NULL OR TRIM(TO_NVARCHAR(CONTACT_LANGUAGE)) = ''
                    THEN '|Sprache leer'
                -- Validität
                WHEN TRIM(TO_NVARCHAR(CONTACT_LANGUAGE)) NOT LIKE_REGEXPR '^[A-Za-z]{2}$'
                    THEN '' --'|Sprache kein zweistelliger Sprachcode'
                -- Einheitlichkeit
                WHEN TO_NVARCHAR(CONTACT_LANGUAGE) <> UPPER(TRIM(TO_NVARCHAR(CONTACT_LANGUAGE)))
                    THEN '|Sprache nicht als Großbuchstaben gepflegt'
                -- Vollständigkeit
                WHEN CONTACT_O_I_D IS NULL OR TRIM(TO_NVARCHAR(CONTACT_O_I_D)) = ''
                    THEN '|Kontakt-Objekt-ID leer'
                -- Validität
                WHEN TO_NVARCHAR(CONTACT_O_I_D) NOT LIKE_REGEXPR '^[A-Za-z0-9._-]+$'
                    THEN '|Kontakt-Objekt-ID ungültiges Format'
                -- Einheitlichkeit
                WHEN TO_NVARCHAR(CONTACT_PAYMENT_METHOD) <> TRIM(TO_NVARCHAR(CONTACT_PAYMENT_METHOD)) OR TO_NVARCHAR(CONTACT_PAYMENT_METHOD_DESC) <> TRIM(TO_NVARCHAR(CONTACT_PAYMENT_METHOD_DESC))
                    THEN '|Zahlungsart mit Rand-Leerzeichen'
                -- Konsistenz
                WHEN COALESCE(TRIM(TO_NVARCHAR(CONTACT_PAYMENT_METHOD_DESC)), '') <> '' AND COALESCE(TRIM(TO_NVARCHAR(CONTACT_PAYMENT_METHOD)), '') = ''
                    THEN '|Zahlungsart fehlt trotz Beschreibung'
                -- Vollständigkeit
                WHEN COALESCE(TRIM(TO_NVARCHAR(CONTACT_PAYMENT_METHOD)), '') <> '' AND COALESCE(TRIM(TO_NVARCHAR(CONTACT_PAYMENT_METHOD_DESC)), '') = ''
                    THEN '|Zahlungsart-Beschreibung leer'
                -- Einheitlichkeit
                WHEN TO_NVARCHAR(CONTACT_SHIPPING_TYPE) <> TRIM(TO_NVARCHAR(CONTACT_SHIPPING_TYPE)) OR TO_NVARCHAR(CONTACT_SHIPPING_TYPE_DESC) <> TRIM(TO_NVARCHAR(CONTACT_SHIPPING_TYPE_DESC))
                    THEN '|Versandart mit Rand-Leerzeichen'
                -- Konsistenz
                WHEN COALESCE(TRIM(TO_NVARCHAR(CONTACT_SHIPPING_TYPE_DESC)), '') <> '' AND COALESCE(TRIM(TO_NVARCHAR(CONTACT_SHIPPING_TYPE)), '') = ''
                    THEN '|Versandart fehlt trotz Beschreibung'
                -- Vollständigkeit
                WHEN COALESCE(TRIM(TO_NVARCHAR(CONTACT_SHIPPING_TYPE)), '') <> '' AND COALESCE(TRIM(TO_NVARCHAR(CONTACT_SHIPPING_TYPE_DESC)), '') = ''
                    THEN '|Versandart-Beschreibung leer'
                -- Einheitlichkeit
                WHEN TO_NVARCHAR(CONTACT_WORK_GROUP) <> TRIM(TO_NVARCHAR(CONTACT_WORK_GROUP))
                    THEN '|Verteilergruppe mit Rand-Leerzeichen'
                -- Validität
                WHEN COALESCE(TO_NVARCHAR(CONTACT_WORK_GROUP), '') <> '' AND TO_NVARCHAR(CONTACT_WORK_GROUP) NOT LIKE_REGEXPR '^[A-Za-z0-9._-]+$'
                    THEN '|Verteilergruppe ungültiges Format'
                ELSE ''
            END
        ) AS DEFICIENCY_DESCRIPTION
    FROM
        joined j
)
SELECT
    -- Kommentieren Sie die folgende Zeile aus, um alles anzuzeigen
    -- TOP 25
    '05'                                                                    AS RULENUMBER,
    'Kontakte-Stammdaten Datenqualitätssicherung'                           AS RULENAME,
    DEFICIENCY_DESCRIPTION                                                  AS RULEDESCRIPTION,
    LENGTH(REPLACE_REGEXPR('[^\\|]' IN DEFICIENCY_DESCRIPTION WITH ''))     AS ERROREVALUATION,
    'VC_Interessent'                                                        AS AREA,
    'Interessent'                                                           AS RULEFIELD,
    REPLACE_REGEXPR('[\.]' IN CAST(contact_i_d AS NVARCHAR(256)) WITH '')   AS IDENTIFIER,
    REPLACE_REGEXPR(
            '\\s+' IN TRIM(
                COALESCE(ADDRESS_NAME,  '') || ' ' || 
                COALESCE(ADDRESS_NAME2, '') || ' ' || 
                COALESCE(ADDRESS_NAME3, '')
            ) WITH ' '
        )                                                              AS DESCRIPTION,
    REPLACE_REGEXPR(
            '\\s+' IN TRIM(
                MASTER_DATA_SUB_TYPE || 
                '|<Firma>' || COMPANY || 
                '|<Kunde>' || contact_customer_i_d ||
                '|<AdressNr>' || contact_adress_no ||
                '|<Verband>' || contact_association ||
                '|<AenderungDatum>' || contact_change_date ||
                '|<AenderungBenutzer>' || contact_change_user ||
                '|<Konzern>' || contact_company_group ||
                '|<AnlageDatum>' || contact_creation_date ||
                '|<AnlageBenutzer>' || contact_creation_user ||
                '|<ZahlungsZiel>' || contact_credit_terms ||
                '|<Rabattgruppe>' || contact_discount_group ||
                '|<RabattArt>' || contact_discount_visible ||
                '|<Branche>' || contact_industry ||
                '|<Sprache>' || contact_language ||
                '|<Name1>' || contact_name ||
                '|<VC_Interessent_Obj>' || contact_o_i_d ||
                '|<ZahlungsArt>' || contact_payment_method ||
                '|<PreisGruppe>' || contact_price_group ||
                '|<Suchbegriff>' || contact_search_term ||
                '|<Selektion>' || contact_selection ||
                '|<VersandArt>' || contact_shipping_type ||
                '|<Sachbearbeiter>' || contact_specialist ||
                '|<VerteilerGruppe>' || contact_work_group ||
                '|<PLZ>' || contact_z_i_p ||
                '|<Postfach>' || address_box ||
                '|<Ort>' || address_city ||
                '|<Staat>' || address_country ||
                '|<EMail>' || address_e_mail ||
                '|<Vorname>' || address_first_name ||
                '|<Name1>' || address_name ||
                '|<Name2>' || address_name2 ||
                '|<Name3>' || address_name3 ||
                '|<S_Adresse_Obj>' || address_o_i_d ||
                '|<Suchbegriff>' || address_search_term ||
                '|<Bundesland>' || address_state ||
                '|<Strasse>' || address_street ||
                '|<Hausnummer>' || address_street_no ||
                '|<Telefon>' || address_telephone ||
                '|<HomePage>' || address_u_r_l ||
                '|<PLZ_Postfach>' || address_z_i_p_box ||
                '|<PLZ>' || address_z_i_p_code
            ) WITH ' '
        )                                                                  AS DESCRIPTION2,
    'Kontakt'                                                               AS CATEGORY,
    CURRENT_DATE                                                            AS ANALYSISDATE,
    COMPANY                                                                 AS COMPANY,
    'Kontakt'                                                               AS FIELDNAME,
    'paSystem'                                                              AS PERSON,
    CASE
        WHEN DEFICIENCY_DESCRIPTION <> '' THEN 'check'
        ELSE 'ok'
    END                                                                     AS STATUS
FROM
    checks
-- Kommentieren Sie die folgende Zeile aus, um alles anzuzeigen
-- WHERE DEFICIENCY_DESCRIPTION <> '' ORDER BY ERROREVALUATION DESC
