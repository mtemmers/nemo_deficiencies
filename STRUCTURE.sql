-- (DEFICIENCIES) Lieferanten
-- Generated: 08.07.2026 08:40:28
-- Prüfungen: 16
-- Regeln: 87 (aktiv: 87, inaktiv: 0)
-- 
--   Block 1: NAME1-3 (Lieferantenname) (5 aktiv / 0 inaktiv)
--   Block 2: ADDRESS_STREET (Straßenname) (5 aktiv / 0 inaktiv)
--   Block 3: ADDRESS_STREET_NO (Hausnummer) (5 aktiv / 0 inaktiv)
--   Block 4: ADDRESS_SEARCH_TERM (Adresse Suchbegriff) (5 aktiv / 0 inaktiv)
--   Block 5: ADDRESS_Z_I_P_CODE (Postleitzahl) (21 aktiv / 0 inaktiv)
--   Block 6: ADDRESS_CITY (Stadt) (5 aktiv / 0 inaktiv)
--   Block 7: ADDRESS_COUNTRY (Land) (3 aktiv / 0 inaktiv)
--   Block 8: ADDRESS_E_MAIL (E-Mail) (5 aktiv / 0 inaktiv)
--   Block 9: ADDRESS_TELEPHONE (Telefon) (5 aktiv / 0 inaktiv)
--   Block 10: ADDRESS_U_R_L (Website) (5 aktiv / 0 inaktiv)
--   Block 11: SUPPLIER_SEARCH_TERM (Lieferanten-Suchbegriff) (5 aktiv / 0 inaktiv)
--   Block 12: SUPPLIER_INDUSTRY (Branche) (7 aktiv / 0 inaktiv)
--   Block 13: SUPPLIER_CREDIT_TERMS_DESC (Zahlungsbedingungen) (1 aktiv / 0 inaktiv)
--   Block 14: SUPPLIER_PAYMENT_METHOD (Zahlungsmethode) (1 aktiv / 0 inaktiv)
--   Block 15: SUPPLIER_CREATION_DATE (Erstellungsdatum) (4 aktiv / 0 inaktiv)
--   Block 16: SUPPLIER_CHANGE_DATE (Änderungsdatum) (5 aktiv / 0 inaktiv)
WITH supp_src AS
     (
             SELECT
                     ADDRESS_I_D
                     , -- #ERP-Origin: S_Adresse.AdressNr
                     SUPPLIER_I_D
                     , -- #ERP-Origin: S_Lieferant.Lieferant
                     MASTER_DATA_SUB_TYPE
                     , -- Typ der Stammdaten (z.B. 'SUPPLIER' für Lieferanten)
                     COMPANY
                     , -- #ERP-Origin: S_Lieferant.Firma
                     address_name
                     , -- #ERP-Origin: S_Adresse.Name1
                     address_name2
                     , -- #ERP-Origin: S_Adresse.Name2
                     address_name3
                     , -- #ERP-Origin: S_Adresse.Name3
                     address_street
                     , -- #ERP-Origin: S_Adresse.Strasse
                     address_street_no
                     , -- #ERP-Origin: S_Adresse.Hausnummer
                     address_search_term
                     , -- #ERP-Origin: S_Adresse.Suchbegriff
                     address_z_i_p_code
                     , -- #ERP-Origin: S_Adresse.PLZ
                     address_city
                     , -- #ERP-Origin: S_Adresse.Ort
                     address_e_mail
                     , -- #ERP-Origin: S_Adresse.EMail
                     address_telephone
                     , -- #ERP-Origin: S_Adresse.Telefon
                     address_u_r_l
                     , -- #ERP-Origin: S_Adresse.HomePage
                     address_box
                     , -- #ERP-Origin: S_Adresse.Postfach
                     address_country
                     , -- #ERP-Origin: S_Adresse.Staat
                     address_first_name
                     , -- #ERP-Origin: S_Adresse.Vorname
                     address_o_i_d
                     , -- #ERP-Origin: S_Adresse.S_Adresse_Obj
                     address_state
                     , -- #ERP-Origin: S_Adresse.Bundesland
                     address_z_i_p_box
                     , -- #ERP-Origin: S_Adresse.PLZ_Postfach
                     SUPPLIER_SEARCH_TERM
                     , SUPPLIER_INDUSTRY
                     , SUPPLIER_CREDIT_TERMS_DESC
                     , SUPPLIER_PAYMENT_METHOD
                     , SUPPLIER_CHANGE_DATE
                     , SUPPLIER_CHANGE_USER
                     , SUPPLIER_CREATION_DATE
                     , SUPPLIER_CREATION_USER
                     ,
                     -- Bereinigter Vollname (NAME1 + NAME2 + NAME3)
                     -- Entfernt mehrfache Leerzeichen
                     REPLACE_REGEXPR( '\\s+' IN TRIM( COALESCE(ADDRESS_NAME, '') || ' ' || COALESCE(ADDRESS_NAME2, '') || ' ' || COALESCE(ADDRESS_NAME3, '') ) WITH ' ' )                                                                                                                                                                                                                                                                                                                                                                                                                 AS FULLNAME_T
                     ,
                     -- Vollständiger Datensatz als strukturierter Text
                     -- Format: FIELD|<TAG>VALUE für alle relevanten Felder
                     REPLACE_REGEXPR( '\\s+' IN TRIM( MASTER_DATA_SUB_TYPE || '|<COMPANY>' || COMPANY || '|<C_SEARCH>' || SUPPLIER_SEARCH_TERM || '|<NAME>' || ADDRESS_NAME || '|<NAME2>' || ADDRESS_NAME2 || '|<NAME3>' || ADDRESS_NAME3 || '|<STREET>' || ADDRESS_STREET || '|<NO>' || ADDRESS_STREET_NO || '|<ZIP>' || ADDRESS_Z_I_P_CODE || '|<CITY>' || ADDRESS_CITY || '|<COUNTRY>' || ADDRESS_COUNTRY || '|<PHONE>' || ADDRESS_TELEPHONE || '|<MAIL>' || ADDRESS_E_MAIL || '|<A_SEARCH>' || ADDRESS_SEARCH_TERM || '|<URL>' || ADDRESS_U_R_L || '|<C_INDUSTRY>' || SUPPLIER_INDUSTRY || '|<C_CREDIT>' || SUPPLIER_CREDIT_TERMS_DESC || '|<C_PAYMENT>' || SUPPLIER_PAYMENT_METHOD ) WITH ' ' ) AS FULL_T
             FROM
                     $schema.$table
             WHERE
                     -- Welche Kategorie
                     UPPER(TRIM(MASTER_DATA_SUB_TYPE)) = 'SUPPLIER' )
                     -- Ausnahmen
                     AND SUPPLIER_I_D not in ('10000000','10000001','10000002','10000003','10000004','10000005','10000006','10000007','10000008','10000009')
     ,
     -- ----------------------------------------------------------------------------
     -- CTE 2: PROZESSRELEVANTE LIEFERANTEN (proc_src)
     -- Identifiziert Lieferanten, die in Geschäftsprozessen tatsächlich verwendet werden
     -- ----------------------------------------------------------------------------
     proc_src AS
     (
             SELECT DISTINCT
                     TRIM(CAST(COMPANY AS NVARCHAR(256)))        AS COMPANY
                     , TRIM(CAST(SUPPLIER_I_D AS NVARCHAR(256))) AS SUPPLIER_I_D
             FROM
                     $schema."pa_export"
             WHERE
                     SUPPLIER_I_D IS NOT NULL )
     ,
     -- ----------------------------------------------------------------------------
     -- CTE 3: GEFILTERTE LIEFERANTEN (joined)
     -- Verknüpft Stammdaten mit prozessrelevanten Lieferanten (INNER JOIN)
     -- Ergebnis: Nur Lieferanten, die auch in Prozessen verwendet werden
     -- ----------------------------------------------------------------------------
     joined AS
     (
             SELECT
                     c.*
             FROM
                     supp_src c
             INNER JOIN
                     proc_src p
             ON
                     c.COMPANY      = p.COMPANY
             AND     c.SUPPLIER_I_D = p.SUPPLIER_I_D )
     ,
     -- ----------------------------------------------------------------------------
     -- CTE 4: DATENQUALITÄTSPRÜFUNGEN (checks)
     -- Führt umfassende Validierungen für alle relevanten Felder durch
     -- ----------------------------------------------------------------------------
     checks AS
     (
             SELECT
                     j.*
                     , (
            -- ================================================================
            -- PRÜFUNG 1: NAME1-3 (Lieferantenname)
            -- ================================================================
            -- NAME1-3 (Lieferantenname)
            -- Beschreibung der Prüfungen die durchgeführt werden | Typen: Ohne Typ
            CASE
                WHEN WHEN
                    FULLNAME_T IS NULL
                    OR FULLNAME_T = ''
                    THEN '|'
                WHEN WHEN
                    ADDRESS_NAME      != TRIM(ADDRESS_NAME)
                    AND ADDRESS_NAME2 != TRIM(ADDRESS_NAME2)
                    AND ADDRESS_NAME3 != TRIM(ADDRESS_NAME3)
                    THEN '|'
                WHEN WHEN
                    FULLNAME_T NOT LIKE_REGEXPR '[\p{L}]' FLAG 'i'
                    THEN '|'
                WHEN WHEN
                    FULLNAME_T NOT LIKE_REGEXPR '^[0-9\p{L}\s\-&\.,/()#:]+' FLAG 'i'
                    THEN '|'
                WHEN WHEN
                    FULLNAME_T LIKE_REGEXPR '([[:<:]]|^)(test|nicht aktiv|inaktiv|inactive|gesperrt|obsolet|veraltet|ungültig|inaktiv|gesperrt|stillgelegt|außer\s+Betrieb|abgelaufen|deaktiviert|gelöscht|archiviert|nicht\s+mehr\s+gültig|historisch|ausgelaufen|beendet|geschlossen|nicht\s+mehr\s+aktiv|ersetzt|überholt|nicht\s+mehr\s+verwendet|obsolete|deprecated|inactive|invalid|expired|deactivated|disabled|deleted|archived|closed|terminated|discontinued|retired|replaced|superseded|outdated|legacy|historical|end-of-life|phased\s+out|suspended|cancelled|canceled|void)([[:>:]]|$)' FLAG 'i'
                    THEN '|'
                ELSE ''
            END ||

            -- ================================================================
            -- PRÜFUNG 2: ADDRESS_STREET (Straßenname)
            -- ================================================================
            -- ADDRESS_STREET (S_Adresse.Strasse)
            -- Beschreibung der Prüfungen die durchgeführt werden | Typen: Ohne Typ
            CASE
                WHEN WHEN
                    TRIM(ADDRESS_STREET) = ''
                    OR ADDRESS_STREET IS NULL
                    THEN '|'
                WHEN WHEN
                    ADDRESS_STREET != TRIM(ADDRESS_STREET)
                    THEN '|'
                WHEN WHEN
                    ADDRESS_STREET NOT LIKE_REGEXPR '[\p{L}]' FLAG 'i'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_STREET NOT LIKE_REGEXPR '^[\p{L}\p{N}\s\.\-'',\/'':&\(\)]*$' FLAG 'i'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_STREET LIKE_REGEXPR '([[:<:]]|^)(test|nicht aktiv|inaktiv|inactive|gesperrt|obsolet|veraltet|ungültig|inaktiv|gesperrt|stillgelegt|außer\s+Betrieb|abgelaufen|deaktiviert|gelöscht|archiviert|nicht\s+mehr\s+gültig|historisch|ausgelaufen|beendet|geschlossen|nicht\s+mehr\s+aktiv|ersetzt|überholt|nicht\s+mehr\s+verwendet|obsolete|deprecated|inactive|invalid|expired|deactivated|disabled|deleted|archived|closed|terminated|discontinued|retired|replaced|superseded|outdated|legacy|historical|end-of-life|phased\s+out|suspended|cancelled|canceled|void)([[:>:]]|$)' FLAG 'i'
                    THEN '|'
                ELSE ''
            END ||

            -- ================================================================
            -- PRÜFUNG 3: ADDRESS_STREET_NO (Hausnummer)
            -- ================================================================
            -- ADDRESS_STREET_NO (S_Adresse.Hausnummer)
            -- Beschreibung der Prüfungen die durchgeführt werden | Typen: Ohne Typ
            CASE
                WHEN WHEN
                    TRIM(ADDRESS_STREET_NO) = ''
                    OR ADDRESS_STREET_NO IS NULL
                    THEN '|'
                WHEN WHEN
                    ADDRESS_STREET_NO != TRIM(ADDRESS_STREET_NO)
                    THEN '|'
                WHEN WHEN
                    ADDRESS_STREET_NO NOT LIKE_REGEXPR '[\p{N}]'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_STREET_NO NOT LIKE_REGEXPR '^\s*\p{N}+[\p{L}\s\-\/\.]*(\p{N}+)?[\p{L}]?$' FLAG 'i'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_STREET_NO LIKE_REGEXPR 'n\.?a\.?' FLAG 'i'
                    THEN '|'
                ELSE ''
            END ||

            -- ================================================================
            -- PRÜFUNG 4: ADDRESS_SEARCH_TERM (Adresse Suchbegriff)
            -- ================================================================
            -- ADDRESS_SEARCH_TERM (S_Adresse.Suchbegriff)
            -- Beschreibung der Prüfungen die durchgeführt werden | Typen: Ohne Typ
            CASE
                WHEN WHEN
                    TRIM(ADDRESS_SEARCH_TERM) = ''
                    OR ADDRESS_SEARCH_TERM IS NULL
                    THEN '|'
                WHEN WHEN
                    ADDRESS_SEARCH_TERM != TRIM(ADDRESS_SEARCH_TERM)
                    THEN '|'
                WHEN WHEN
                    ADDRESS_SEARCH_TERM NOT LIKE_REGEXPR '[\p{L}]' FLAG 'i'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_SEARCH_TERM NOT LIKE_REGEXPR '[0-9\p{L}\s-]' FLAG 'i'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_SEARCH_TERM LIKE_REGEXPR '([[:<:]]|^)(test|nicht aktiv|inaktiv|inactive|gesperrt|obsolet|veraltet|ungültig|inaktiv|gesperrt|stillgelegt|außer\s+Betrieb|abgelaufen|deaktiviert|gelöscht|archiviert|nicht\s+mehr\s+gültig|historisch|ausgelaufen|beendet|geschlossen|nicht\s+mehr\s+aktiv|ersetzt|überholt|nicht\s+mehr\s+verwendet|obsolete|deprecated|inactive|invalid|expired|deactivated|disabled|deleted|archived|closed|terminated|discontinued|retired|replaced|superseded|outdated|legacy|historical|end-of-life|phased\s+out|suspended|cancelled|canceled|void)([[:>:]]|$)' FLAG 'i'
                    THEN '|'
                ELSE ''
            END ||

            -- ================================================================
            -- PRÜFUNG 5: ADDRESS_Z_I_P_CODE (Postleitzahl)
            -- ================================================================
            -- ADDRESS_Z_I_P_CODE (S_Adresse.PLZ)
            -- Beschreibung der Prüfungen die durchgeführt werden | Typen: Ohne Typ
            CASE
                WHEN WHEN
                    TRIM(ADDRESS_Z_I_P_CODE) = ''
                    OR ADDRESS_Z_I_P_CODE IS NULL
                    THEN '|'
                WHEN WHEN
                    ADDRESS_Z_I_P_CODE != TRIM(ADDRESS_Z_I_P_CODE)
                    THEN '|'
                WHEN WHEN
                    ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '[\p{N}]'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_COUNTRY              = 'NL'
                    AND TRIM(ADDRESS_Z_I_P_CODE) <> ''
                    AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[\p{N}]{4}[\s]?[A-Za-z]{2}$'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_COUNTRY              = 'PL'
                    AND TRIM(ADDRESS_Z_I_P_CODE) <> ''
                    AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[\p{N}]{2}-?[\p{N}]{3}$'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_COUNTRY              = 'PT'
                    AND TRIM(ADDRESS_Z_I_P_CODE) <> ''
                    AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[\p{N}]{4}-?[\p{N}]{3}$'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_COUNTRY              = 'GB'
                    AND TRIM(ADDRESS_Z_I_P_CODE) <> ''
                    AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[A-Za-z]{1,2}[\p{N}][A-Za-z0-9]?[\s]?[\p{N}][A-Za-z]{2}$'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_COUNTRY              = 'CA'
                    AND TRIM(ADDRESS_Z_I_P_CODE) <> ''
                    AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[A-Za-z][\p{N}][A-Za-z][\s]?[\p{N}][A-Za-z][\p{N}]$'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_COUNTRY              = 'JP'
                    AND TRIM(ADDRESS_Z_I_P_CODE) <> ''
                    AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[\p{N}]{3}-?[\p{N}]{4}$'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_COUNTRY              = 'TW'
                    AND TRIM(ADDRESS_Z_I_P_CODE) <> ''
                    AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[\p{N}]{3}([\p{N}]{2})?$'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_COUNTRY              = 'BR'
                    AND TRIM(ADDRESS_Z_I_P_CODE) <> ''
                    AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^([\p{N}]{8}|[\p{N}]{5}-[\p{N}]{3})$'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_COUNTRY              = 'IE'
                    AND TRIM(ADDRESS_Z_I_P_CODE) <> ''
                    AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[A-Za-z][0-9A-Za-z][0-9A-Za-z][\s]?[0-9A-Za-z]{4}$'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_COUNTRY              = 'AR'
                    AND TRIM(ADDRESS_Z_I_P_CODE) <> ''
                    AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^([A-Za-z][\p{N}]{4}[A-Za-z]{3}|[\p{N}]{4})$'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_COUNTRY              = 'CZ'
                    AND TRIM(ADDRESS_Z_I_P_CODE) <> ''
                    AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[\p{N}]{3}[\s]?[\p{N}]{2}$'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_COUNTRY              = 'SK'
                    AND TRIM(ADDRESS_Z_I_P_CODE) <> ''
                    AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[\p{N}]{3}[\s]?[\p{N}]{2}$'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_COUNTRY IN ( 'D', 'DE', 'ES', 'FR', 'IT', 'US', 'MX', 'MA', 'DZ', 'EG', 'GR', 'TR', 'UA', 'TH', 'MY', 'PH', 'PE', 'JO', 'SA', 'TN', 'MK', 'GT', 'HN', 'NI', 'SV', 'CR', 'PA', 'VE', 'GE', 'LT', 'LV' )
                    AND TRIM(ADDRESS_Z_I_P_CODE) <> ''
                    AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[\p{N}]{5}$'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_COUNTRY IN ( 'AT', 'CH', 'DK', 'NO', 'SE', 'BE', 'LU', 'LI', 'IS', 'AU', 'BA', 'ME', 'MM', 'KH', 'LA', 'NP' )
                    AND TRIM(ADDRESS_Z_I_P_CODE) <> ''
                    AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[\p{N}]{4}$'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_COUNTRY IN ( 'RU', 'CN', 'IN', 'KZ', 'KG', 'UZ', 'TJ', 'TM', 'VN', 'BY', 'SG', 'CO', 'CL' )
                    AND TRIM(ADDRESS_Z_I_P_CODE) <> ''
                    AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[\p{N}]{6}$'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_COUNTRY IN ('IR')
                    AND TRIM(ADDRESS_Z_I_P_CODE) <> ''
                    AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[\p{N}]{7}$'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_COUNTRY IN ('IS')
                    AND TRIM(ADDRESS_Z_I_P_CODE) <> ''
                    AND ADDRESS_Z_I_P_CODE NOT LIKE_REGEXPR '^[\p{N}]{3}$'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_Z_I_P_CODE LIKE_REGEXPR '(00000|99999)'
                    THEN '|'
                ELSE ''
            END ||

            -- ================================================================
            -- PRÜFUNG 6: ADDRESS_CITY (Stadt)
            -- ================================================================
            -- ADDRESS_CITY (S_Adresse.Ort)
            -- Beschreibung der Prüfungen die durchgeführt werden | Typen: Ohne Typ
            CASE
                WHEN WHEN
                    TRIM(ADDRESS_CITY) = ''
                    OR ADDRESS_CITY IS NULL
                    THEN '|'
                WHEN WHEN
                    ADDRESS_CITY != TRIM(ADDRESS_CITY)
                    THEN '|'
                WHEN WHEN
                    ADDRESS_CITY NOT LIKE_REGEXPR '[\p{L}]' FLAG 'i'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_CITY NOT LIKE_REGEXPR '^[\p{L}\p{N}\s\.\-'',\/'':&\(\)]*$'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_CITY LIKE_REGEXPR '([[:<:]]|^)(test|nicht aktiv|inaktiv|inactive|gesperrt|obsolet|veraltet|ungültig|inaktiv|gesperrt|stillgelegt|außer\s+Betrieb|abgelaufen|deaktiviert|gelöscht|archiviert|nicht\s+mehr\s+gültig|historisch|ausgelaufen|beendet|geschlossen|nicht\s+mehr\s+aktiv|ersetzt|überholt|nicht\s+mehr\s+verwendet|obsolete|deprecated|inactive|invalid|expired|deactivated|disabled|deleted|archived|closed|terminated|discontinued|retired|replaced|superseded|outdated|legacy|historical|end-of-life|phased\s+out|suspended|cancelled|canceled|void)([[:>:]]|$)' FLAG 'i'
                    THEN '|'
                ELSE ''
            END ||

            -- ================================================================
            -- PRÜFUNG 7: ADDRESS_COUNTRY (Land)
            -- ================================================================
            -- ADDRESS_COUNTRY (S_Adresse.Staat)
            -- Beschreibung der Prüfungen die durchgeführt werden | Typen: Ohne Typ
            CASE
                WHEN WHEN
                    TRIM(ADDRESS_COUNTRY) = ''
                    OR ADDRESS_COUNTRY IS NULL
                    THEN '|'
                WHEN WHEN
                    ADDRESS_COUNTRY != TRIM(ADDRESS_COUNTRY)
                    THEN '|'
                WHEN WHEN
                    ADDRESS_COUNTRY NOT LIKE_REGEXPR '^[A-Z]{2}$'
                    THEN '|'
                ELSE ''
            END ||

            -- ================================================================
            -- PRÜFUNG 8: ADDRESS_E_MAIL (E-Mail)
            -- ================================================================
            -- ADDRESS_E_MAIL (S_Adresse.EMail)
            -- Beschreibung der Prüfungen die durchgeführt werden | Typen: Ohne Typ
            CASE
                WHEN WHEN
                    TRIM(ADDRESS_E_MAIL) = ''
                    OR ADDRESS_E_MAIL IS NULL
                    THEN '|'
                WHEN WHEN
                    ADDRESS_E_MAIL != TRIM(ADDRESS_E_MAIL)
                    THEN '|'
                WHEN WHEN
                    ADDRESS_E_MAIL NOT LIKE_REGEXPR '[\p{L}@]' FLAG 'i'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_E_MAIL NOT LIKE_REGEXPR '^[\p{L}\p{N}._%+-]+@[\p{L}\p{N}.-]+\.[\p{L}]{2,}$' FLAG 'i'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_E_MAIL LIKE_REGEXPR '([[:<:]]|^)(test|nicht aktiv|inaktiv|inactive|gesperrt|obsolet|veraltet|ungültig|inaktiv|gesperrt|stillgelegt|außer\s+Betrieb|abgelaufen|deaktiviert|gelöscht|archiviert|nicht\s+mehr\s+gültig|historisch|ausgelaufen|beendet|geschlossen|nicht\s+mehr\s+aktiv|ersetzt|überholt|nicht\s+mehr\s+verwendet|obsolete|deprecated|inactive|invalid|expired|deactivated|disabled|deleted|archived|closed|terminated|discontinued|retired|replaced|superseded|outdated|legacy|historical|end-of-life|phased\s+out|suspended|cancelled|canceled|void)([[:>:]]|$)' FLAG 'i'
                    THEN '|'
                ELSE ''
            END ||

            -- ================================================================
            -- PRÜFUNG 9: ADDRESS_TELEPHONE (Telefon)
            -- ================================================================
            -- ADDRESS_TELEPHONE (S_Adresse.Telefon)
            -- Beschreibung der Prüfungen die durchgeführt werden | Typen: Ohne Typ
            CASE
                WHEN WHEN
                    TRIM(TO_VARCHAR(ADDRESS_TELEPHONE)) = ''
                    OR ADDRESS_TELEPHONE IS NULL
                    THEN '|'
                WHEN WHEN
                    ADDRESS_TELEPHONE != TRIM(ADDRESS_TELEPHONE)
                    THEN '|'
                WHEN WHEN
                    ADDRESS_TELEPHONE NOT LIKE_REGEXPR '[\p{N}]'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_TELEPHONE NOT LIKE_REGEXPR '^\+?[1-9][0-9]{5,14}$'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_TELEPHONE LIKE_REGEXPR '([[:<:]]|^)(test|nicht aktiv|inaktiv|inactive|gesperrt|obsolet|veraltet|ungültig|inaktiv|gesperrt|stillgelegt|außer\s+Betrieb|abgelaufen|deaktiviert|gelöscht|archiviert|nicht\s+mehr\s+gültig|historisch|ausgelaufen|beendet|geschlossen|nicht\s+mehr\s+aktiv|ersetzt|überholt|nicht\s+mehr\s+verwendet|obsolete|deprecated|inactive|invalid|expired|deactivated|disabled|deleted|archived|closed|terminated|discontinued|retired|replaced|superseded|outdated|legacy|historical|end-of-life|phased\s+out|suspended|cancelled|canceled|void)([[:>:]]|$)' FLAG 'i'
                    THEN '|'
                ELSE ''
            END ||

            -- ================================================================
            -- PRÜFUNG 10: ADDRESS_U_R_L (Website)
            -- ================================================================
            -- ADDRESS_U_R_L (S_Adresse.HomePage)
            -- Beschreibung der Prüfungen die durchgeführt werden | Typen: Ohne Typ
            CASE
                WHEN WHEN
                    TRIM(ADDRESS_U_R_L) = ''
                    OR ADDRESS_U_R_L IS NULL
                    THEN '|'
                WHEN WHEN
                    ADDRESS_U_R_L != TRIM(ADDRESS_U_R_L)
                    THEN '|'
                WHEN WHEN
                    ADDRESS_U_R_L NOT LIKE_REGEXPR '[\p{L}]' FLAG 'i'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_U_R_L NOT LIKE_REGEXPR '^(https?://)?([a-zA-Z0-9-]+\.){1,}([a-zA-Z]{2,})(\/[^\s]*)?$'
                    THEN '|'
                WHEN WHEN
                    ADDRESS_U_R_L LIKE_REGEXPR '([[:<:]]|^)(test|nicht aktiv|inaktiv|inactive|gesperrt|obsolet|veraltet|ungültig|inaktiv|gesperrt|stillgelegt|außer\s+Betrieb|abgelaufen|deaktiviert|gelöscht|archiviert|nicht\s+mehr\s+gültig|historisch|ausgelaufen|beendet|geschlossen|nicht\s+mehr\s+aktiv|ersetzt|überholt|nicht\s+mehr\s+verwendet|obsolete|deprecated|inactive|invalid|expired|deactivated|disabled|deleted|archived|closed|terminated|discontinued|retired|replaced|superseded|outdated|legacy|historical|end-of-life|phased\s+out|suspended|cancelled|canceled|void)([[:>:]]|$)' FLAG 'i'
                    THEN '|'
                ELSE ''
            END ||

            -- ================================================================
            -- PRÜFUNG 11: SUPPLIER_SEARCH_TERM (Lieferanten-Suchbegriff)
            -- ================================================================
            -- SUPPLIER_SEARCH_TERM (Lieferanten-Suchbegriff)
            -- Beschreibung der Prüfungen die durchgeführt werden | Typen: Ohne Typ
            CASE
                WHEN WHEN
                    TRIM(SUPPLIER_SEARCH_TERM) = ''
                    OR SUPPLIER_SEARCH_TERM IS NULL
                    THEN '|'
                WHEN WHEN
                    SUPPLIER_SEARCH_TERM != TRIM(SUPPLIER_SEARCH_TERM)
                    THEN '|'
                WHEN WHEN
                    SUPPLIER_SEARCH_TERM NOT LIKE_REGEXPR '[\p{L}]' FLAG 'i'
                    THEN '|'
                WHEN WHEN
                    SUPPLIER_SEARCH_TERM NOT LIKE_REGEXPR '[0-9\p{L}\s-]' FLAG 'i'
                    THEN '|'
                WHEN WHEN
                    SUPPLIER_SEARCH_TERM LIKE_REGEXPR '([[:<:]]|^)(test|nicht aktiv|inaktiv|inactive|gesperrt|obsolet|veraltet|ungültig|inaktiv|gesperrt|stillgelegt|außer\s+Betrieb|abgelaufen|deaktiviert|gelöscht|archiviert|nicht\s+mehr\s+gültig|historisch|ausgelaufen|beendet|geschlossen|nicht\s+mehr\s+aktiv|ersetzt|überholt|nicht\s+mehr\s+verwendet|obsolete|deprecated|inactive|invalid|expired|deactivated|disabled|deleted|archived|closed|terminated|discontinued|retired|replaced|superseded|outdated|legacy|historical|end-of-life|phased\s+out|suspended|cancelled|canceled|void)([[:>:]]|$)' FLAG 'i'
                    THEN '|'
                ELSE ''
            END ||

            -- ================================================================
            -- PRÜFUNG 12: SUPPLIER_INDUSTRY (Branche)
            -- ================================================================
            -- SUPPLIER_INDUSTRY (Branche)
            -- Beschreibung der Prüfungen die durchgeführt werden | Typen: Ohne Typ
            CASE
                WHEN WHEN
                    TRIM(SUPPLIER_INDUSTRY) = ''
                    OR SUPPLIER_INDUSTRY IS NULL
                    THEN '|'
                WHEN WHEN
                    SUPPLIER_INDUSTRY != TRIM(SUPPLIER_INDUSTRY)
                    THEN '|'
                WHEN WHEN
                    SUPPLIER_INDUSTRY NOT LIKE_REGEXPR '^[a-z0-9]+$' FLAG 'i'
                    THEN '|'
                WHEN WHEN
                    UPPER(TRIM(SUPPLIER_INDUSTRY)) NOT IN ( 'AMB','ASM' )
                    THEN '|'
                WHEN WHEN
                    UPPER(TRIM(SUPPLIER_INDUSTRY)) IN ('AB','BC','CD')
                    THEN '|'
                WHEN WHEN
                    SUPPLIER_INDUSTRY = LOWER(SUPPLIER_INDUSTRY)
                    THEN '|'
                WHEN WHEN
                    SUPPLIER_INDUSTRY != UPPER(SUPPLIER_INDUSTRY)
                    THEN '|'
                ELSE ''
            END ||

            -- ================================================================
            -- PRÜFUNG 13: SUPPLIER_CREDIT_TERMS_DESC (Zahlungsbedingungen)
            -- ================================================================
            -- SUPPLIER_CREDIT_TERMS_DESC (Zahlungsbedingungen)
            -- Beschreibung der Prüfungen die durchgeführt werden | Typen: Ohne Typ
            CASE
                WHEN WHEN
                    TRIM(SUPPLIER_CREDIT_TERMS_DESC) = ''
                    OR SUPPLIER_CREDIT_TERMS_DESC IS NULL
                    THEN '|'
                ELSE ''
            END ||

            -- ================================================================
            -- PRÜFUNG 14: SUPPLIER_PAYMENT_METHOD (Zahlungsmethode)
            -- ================================================================
            -- SUPPLIER_PAYMENT_METHOD (Zahlungsmethode)
            -- Beschreibung der Prüfungen die durchgeführt werden | Typen: Ohne Typ
            CASE
                WHEN WHEN
                    TRIM(SUPPLIER_PAYMENT_METHOD) = ''
                    OR SUPPLIER_PAYMENT_METHOD IS NULL
                    THEN '|'
                ELSE ''
            END ||

            -- ================================================================
            -- PRÜFUNG 15: SUPPLIER_CREATION_DATE (Erstellungsdatum)
            -- Validiert Erstellungsdatum des Lieferanten-Stammsatzes
            -- ================================================================
            -- SUPPLIER_CREATION_DATE (Erstellungsdatum)
            -- Validiert Erstellungsdatum des Lieferanten-Stammsatzes | Typen: Ohne Typ
            CASE
                WHEN WHEN
                    SUPPLIER_CREATION_DATE IS NULL
                    THEN '|'
                WHEN WHEN
                    SUPPLIER_CREATION_DATE > CURRENT_DATE
                    THEN '|'
                WHEN WHEN
                    DAYS_BETWEEN(SUPPLIER_CREATION_DATE, CURRENT_DATE) / 365 > 100
                    THEN '|'
                WHEN WHEN
                    SUPPLIER_CREATION_DATE < CAST('1900-01-01' AS DATE)
                    THEN '|'
                ELSE ''
            END ||

            -- ================================================================
            -- PRÜFUNG 16: SUPPLIER_CHANGE_DATE (Änderungsdatum)
            -- Validiert Änderungsdatum des Lieferanten-Stammsatzes
            -- ================================================================
            -- SUPPLIER_CHANGE_DATE (Änderungsdatum)
            -- Validiert Änderungsdatum des Lieferanten-Stammsatzes | Typen: Ohne Typ
            CASE
                WHEN WHEN
                    SUPPLIER_CHANGE_DATE IS NULL
                    THEN '|'
                WHEN WHEN
                    SUPPLIER_CHANGE_DATE > CURRENT_DATE
                    THEN '|'
                WHEN WHEN
                    SUPPLIER_CHANGE_DATE < SUPPLIER_CREATION_DATE
                    THEN '|'
                WHEN WHEN
                    DAYS_BETWEEN(SUPPLIER_CHANGE_DATE, CURRENT_DATE) / 365 > 100
                    THEN '|'
                WHEN WHEN
                    SUPPLIER_CHANGE_DATE < CAST('1900-01-01' AS DATE)
                    THEN '|'
                ELSE ''
            END
        ) AS DEFICIENCY_DESCRIPTION
             FROM
                     joined j )
SELECT
        -- Ausgabe der finalen Mängelliste mit relevanten Informationen für die Datenqualitätsanalyse
        -- TOP 25
        '02'                                                                AS RULENUMBER
        , 'Lieferanten-Stammdaten Datenqualitätssicherung'                  AS RULENAME
        , DEFICIENCY_DESCRIPTION                                            AS RULEDESCRIPTION
        , LENGTH(REPLACE_REGEXPR('[^|]' IN deficiency_description WITH '')) AS ERROREVALUATION
        , 'S_Lieferant'                                                     AS AREA
        , 'Lieferant'                                                       AS RULEFIELD
        , REPLACE_REGEXPR('\.' IN SUPPLIER_I_D WITH '')                     AS IDENTIFIER
        , FULLNAME_T                                                        AS DESCRIPTION
        , FULL_T                                                            AS DESCRIPTION2
        , 'Supplier'                                                        AS CATEGORY
        , CURRENT_DATE                                                      AS ANALYSISDATE
        , COMPANY                                                           AS COMPANY
        , 'Lieferant'                                                       AS FIELDNAME
        , 'paSystem'                                                        AS PERSON
        , (
                CASE
                WHEN
                        DEFICIENCY_DESCRIPTION != ''
                THEN
                        'check'
                ELSE
                        'ok'
                END )                                                       AS STATUS
FROM
        checks
        -- Auskommentieren, wenn nur die Lieferanten mit Mängeln ausgegeben werden sollen
        -- WHERE DEFICIENCY_DESCRIPTION <> '' ORDER BY ERROREVALUATION DESC