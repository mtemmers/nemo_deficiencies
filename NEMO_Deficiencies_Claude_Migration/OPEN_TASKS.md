# Offene Aufgaben

## Aktuell offen

### PRO-CL00351-Arbeitsstand konsolidieren

Kontext: Im aktuellen Arbeitsbaum liegen viele ungetrackte Dateien mit `PRO-CL00351` sowie `rulebook_export.py` und `tests/test_rulebook_export.py`. Diese Dateien enthalten offenbar den neueren Regelwerksbericht-Stand mit PDF/Excel und Zusatzabhaengigkeiten.

Aufgabe:

- Diffs zwischen Hauptdateien und `*-PRO-CL00351.*` pruefen.
- Entscheiden, ob PRO-Stand in Hauptdateien uebernommen werden soll.
- Falls ja: Hauptdateien gezielt mergen, keine fremden Aenderungen verwerfen.
- `pyproject.toml` und `requirements.txt` um `openpyxl>=3.1,<4` und `reportlab>=4.2,<5` ergaenzen, falls Regelwerksbericht aktiv bleibt.
- Tests aktualisieren und ausfuehren.

### Vollstaendigen aktuellen Testlauf ausfuehren

Kontext: Historische Teststaende sind 145, 164 und 167 bestandene Tests. Der aktuelle Arbeitsbaum hat ungetrackte neue Dateien, daher muss neu geprueft werden.

Aufgabe:

- Entwicklungsumgebung aktivieren oder einrichten.
- Abhaengigkeiten pruefen.
- Kompletten Testlauf starten.
- Ergebnis in `Plan.md` dokumentieren.

### Git- und Release-Stand klaeren

Kontext: Git-Status zeigte `main...origin/main` und ungetrackte Dateien. Ein Commit/Push darf nur auf ausdrueckliche Freigabe erfolgen.

Aufgabe:

- `git status` und relevante Diffs ansehen.
- Keine Dateien loeschen oder resetten.
- Benutzer fragen, bevor Commit, Tag, Push oder Release erfolgt.

### Zugangsdatenrotation bestaetigen

Kontext: Fruehere lokale Klartext-Konfigurationen wurden entfernt. Es gab Hinweise, dass alte Git-Historie frueher Config-Dateien enthalten haben koennte. Das aktuelle Entfernen macht frueher offengelegte Geheimnisse nicht geheim.

Aufgabe:

- Benutzer daran erinnern, frueher verwendete NEMO-Passwoerter/API-Keys zu rotieren, falls noch nicht geschehen.
- Keine geheimen Werte anzeigen oder in Dateien schreiben.

## Als Naechstes sinnvoll

### Berichtsinventar fuer Master Data erstellen

Kontext: `Plan.md` fordert ein Inventar mit Dateiname, Reportname, Sub-Type und Regelanzahl.

Aufgabe:

- Alle SQL-Dateien in `Master Data` analysieren.
- TOP-25-Berichte nicht als eigene fachliche Quellen behandeln.
- Parser nutzen statt reiner Stringsuche, wo moeglich.
- Ergebnis dokumentieren.

### Parser-/Generator-Roundtrips fuer alle Master-Data-Berichte

Kontext: Ziel ist ein fachlich gepruefter Ausgangsbestand.

Aufgabe:

- Jeden relevanten `(DEFICIENCIES)`-Bericht mit Editor-Parser laden.
- SQL-Generator-Roundtrip ausfuehren.
- Diff zum Ausgangsbestand pruefen.
- Abweichungen zwischen Headerstatistik und erkannten Regeln dokumentieren.

### `(DEFICIENCIES) Adressen`: offene Feldarbeit

Kontext: Adressen ist aktueller fachlicher Schwerpunkt.

Aufgaben:

- `ADDRESS_STATE` in `DESCRIPTION2` ergaenzen.
- Entscheidung treffen, ob `ADDRESS_I_D` zusaetzlich zu separater Ausgabe als `IDENTIFIER` auch in `DESCRIPTION2` stehen soll.
- Attribute und Quellprojektion vollstaendig pruefen.
- Uebrige Regelgruppen fachlich pruefen.
- Gemeinsame Adressfelder mit Contacts/Customers/Suppliers vergleichen.
- Gueltige und ungueltige Beispieldaten fuer kritische Regeln testen.

### Mehrfeld-Regelgruppen technisch umsetzen

Kontext: Name-1-3-Regeln wurden von Hilfsfeldern auf Originalfelder umgestellt, sind aber noch ausgeschrieben. Gewuenscht sind kompakte Mehrfeld-Vorlagen.

Aufgabe:

- Modell von nur `internalName` auf optional `fields` erweitern.
- Editor soll Namensregeln einmalig als `{field}`-Vorlagen anzeigen.
- Aggregation je Regel definieren: `ANY` oder `ALL`.
- SQL-Generator soll Mehrfeld-Vorlagen erst bei Ausgabe auf die Originalfelder erweitern.
- Parser-Markierung einbauen, damit kompakte Darstellung nach erneutem Laden erhalten bleibt.
- Bestehende Dreifachbedingungen danach kontrolliert ersetzen.

## Spaeter / optional

### KI-Ausbau

- Kosten-, Token- und Laufzeituebersicht.
- Anbieterabhaengige Modellprofile.
- Fallback-Reihenfolge ueber mehrere Anbieter.

### Regelkatalog und Harmonisierung

- Bestehende Regeln vollstaendig in generische Katalogregeln ueberfuehren.
- Fachlich freigegebenen Standard je gemeinsamem Feld definieren.
- Harmonisierung ueber mehrere NEMO-Projekte und Tenants.
- Abweichende Reports kontrolliert an Standards angleichen.

### Sprache und Benennung

- Deutsche und englische Fehlermeldungen vollstaendig pruefen.
- Muster `Feld: Fehlermeldung` konsequent durchsetzen.
- Umlaute und `ß` in deutschen Ausgaben einheitlich verwenden.
- Ersatzschreibweisen wie `ae`, `oe`, `ue` entfernen, wo fachlich richtig.
- Begriffe wie `Obsolet`, `Testwert`, `Ungueltig` und `Leer` vereinheitlichen.
- Uebersetzungscache nach Aenderungen gezielt aktualisieren.

### Abnahme und Verteilung

- Vollstaendigen automatisierten Testlauf ausfuehren.
- SQL-Diff gegen Ausgangsbestand pruefen.
- Fachliche Stichproben mit gueltigen und ungueltigen Beispieldaten.
- SQL zuerst in Test-Konfiguration nach NEMO schreiben.
- Hauptbericht und TOP-25-Partner ausfuehren.
- Fachliche Freigabe einholen.
- Git-Commit und neue Version nur nach Freigabe.
- Freigegebene Berichte von Testumgebung auf weitere Tenants spiegeln.

## Ungeklaert

- Ob die `PRO-CL00351`-Dateien als dauerhafter Feature-Branch, Sicherungskopie oder versehentlich liegengebliebener Arbeitsstand gedacht sind.
- Ob frueher verwendete Zugangsdaten bereits vollstaendig rotiert wurden.
- Ob der neue Regelwerksbericht bereits in den aktuell veroeffentlichten GitHub-Release eingeflossen ist oder nur lokal/untracked vorliegt.
- Ob vollstaendige ChatGPT-Projektgespraeche ausserhalb sichtbarer Codex-Zusammenfassungen noch separat exportiert und Claude gegeben werden sollen.
