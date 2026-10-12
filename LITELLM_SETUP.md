# LiteLLM Integration in NEMO Deficiencies

## Überblick

Die NEMO Deficiencies Anwendung unterstützt jetzt **LiteLLM** als KI-Provider. LiteLLM ist ein Proxy für verschiedene LLM-Provider und ermöglicht es Ihnen, einfach zwischen verschiedenen Modellen und Anbietern zu wechseln.

## Konfiguration

### 1. LiteLLM installieren und starten

```bash
# LiteLLM installieren
pip install litellm

# LiteLLM Server starten (Standard Port: 8000)
# Wenn Port 8000 verwendet wird, können Sie einen anderen verwenden:
litellm --port 4000
```

### 2. In der Anwendung konfigurieren

1. **KI-Zugang einrichten** - Button in der Anwendung
2. **Anbieter wählen**: `LiteLLM`
3. **Einstellungen**:
   - **API-Adresse**: `http://localhost:4000/v1` (Standard-Port)
   - **Modell**: Das LLM-Modell, das Sie verwenden möchten (z.B. `gpt-3.5-turbo`)
   - **API-Key**: Optional (nur wenn erforderlich)

### 3. LiteLLM Konfiguration

Erstellen Sie eine `litellm_config.yaml` in Ihrem Unternehmensnetzwerk:

```yaml
model_list:
  - model_name: gpt-3.5-turbo
    litellm_params:
      model: openai/gpt-3.5-turbo
      api_key: $OPENAI_API_KEY
      api_base: https://api.openai.com/v1

  - model_name: claude-3-opus
    litellm_params:
      model: claude-3-opus-20240229
      api_key: $ANTHROPIC_API_KEY
      api_base: https://api.anthropic.com

  - model_name: local-llama
    litellm_params:
      model: ollama/llama2
      api_base: http://localhost:11434/v1
```

Starten Sie LiteLLM mit der Konfiguration:

```bash
litellm --config ./litellm_config.yaml --port 4000
```

## Unterstützte Provider durch LiteLLM

Mit LiteLLM können Sie folgende Provider nutzen:

- OpenAI (GPT-3.5, GPT-4, etc.)
- Anthropic (Claude)
- Google (Gemini)
- Microsoft Azure
- Ollama (lokal)
- LM Studio (lokal)
- Hugging Face
- Replicate
- und viele mehr...

## Umgebungsvariablen

Setzen Sie die erforderlichen API-Keys als Umgebungsvariablen:

```powershell
# PowerShell
$env:OPENAI_API_KEY = "your-api-key"
$env:ANTHROPIC_API_KEY = "your-api-key"
```

```bash
# Linux/macOS
export OPENAI_API_KEY="your-api-key"
export ANTHROPIC_API_KEY="your-api-key"
```

## Troubleshooting

### Port bereits in Verwendung
```powershell
.\kill-port.ps1  # Beendet Prozesse auf Port 8000
```

### LiteLLM-Verbindung fehlgeschlagen
- Überprüfen Sie, ob LiteLLM läuft: `http://localhost:4000/docs`
- Überprüfen Sie die API-Adresse in der Anwendung
- Überprüfen Sie die Netzwerk-Verbindung

### Modell nicht unterstützt
- Überprüfen Sie die LiteLLM-Konfiguration
- Stellen Sie sicher, dass das Modell in der `litellm_config.yaml` definiert ist

## Weitere Informationen

- [LiteLLM Dokumentation](https://docs.litellm.ai/)
- [LiteLLM GitHub](https://github.com/BerriAI/litellm)
- [NEMO Deficiencies Dokumentation](./README.md)
