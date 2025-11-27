// esp32_balanca.ino
#include <WiFi.h>
#include <HTTPClient.h>
#include "HX711.h"

// ====== CONFIG ======
const char* WIFI_SSID = "SEU_WIFI";
const char* WIFI_PASSWORD = "SUA_SENHA";

const char* SERVER_URL = "http://SEU_IP_DO_SERVIDOR:8000/api/weight";

// HX711 pinos
#define PIN_DOUT  4
#define PIN_SCK   5

HX711 balanca;

// intervalo leitura (ms)
unsigned long intervaloLeitura = 5000;
unsigned long ultimaLeitura = 0;

// peso salvo (maior já registrado ou último salvo conforme regras)
// inicializar com 0; se quiser restaurar entre reinicios, implementar armazenamento em SPIFFS/EEPROM
float pesoSalvo = 0.0;

void setup() {
  Serial.begin(115200);
  delay(200);

  balanca.begin(PIN_DOUT, PIN_SCK);
  Serial.println("Inicializando HX711...");
  delay(500);

  if (!balanca.is_ready()) {
    Serial.println("Erro: HX711 não respondeu!");
    // não trava; tenta continuar
  } else {
    Serial.println("HX711 pronto.");
  }

  // conecta WiFi
  Serial.printf("Conectando a WiFi %s\n", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 20000) {
    delay(500);
    Serial.print(".");
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi conectado!");
    Serial.print("IP: "); Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nFalha ao conectar WiFi.");
  }
}

void loop() {
  unsigned long agora = millis();
  if (agora - ultimaLeitura < intervaloLeitura) return;
  ultimaLeitura = agora;

  if (!balanca.is_ready()) {
    Serial.println("HX711 não pronto na leitura, pulando.");
    return;
  }

  // Lê valor bruto (média pode melhorar estabilidade)
  long leitura = balanca.read_average(5); // média de 5 leituras
  float pesoAtual = (float)leitura;

  Serial.println("---------------------------");
  Serial.printf("Peso atual (raw): %.2f\n", pesoAtual);
  Serial.printf("Peso salvo (raw): %.2f\n", pesoSalvo);

  // regra 1: novo maior => só atualiza
  if (pesoAtual > pesoSalvo) {
    Serial.println("Novo maior peso detectado -> atualizando pesoSalvo (sem envio).");
    pesoSalvo = pesoAtual;
    return;
  }

  // regra 2: nova leitura menor -> enviar diferença e atualizar pesoSalvo
  if (pesoAtual < pesoSalvo) {
    float diferenca = pesoSalvo - pesoAtual;
    Serial.printf("Queda detectada. Diferença = %.2f -> enviando...\n", diferenca);

    bool enviado = enviarParaServidor(diferenca, pesoAtual);
    if (enviado) {
      Serial.println("Enviado com sucesso. Atualizando pesoSalvo para pesoAtual.");
      pesoSalvo = pesoAtual;
    } else {
      Serial.println("Falha no envio. Mantendo pesoSalvo (pode reenviar depois se desejar).");
      // opcional: não atualizar pesoSalvo para tentar reenviar mais tarde
      // se preferir atualizar mesmo com falha, descomente:
      // pesoSalvo = pesoAtual;
    }
    return;
  }

  // peso igual -> nada a fazer
  Serial.println("Peso igual -> nada a fazer.");
}

bool enviarParaServidor(float diferenca, float pesoAtual) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi desconectado, tentando reconectar...");
    WiFi.reconnect();
    unsigned long start = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - start < 10000) {
      delay(200);
    }
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("Falha ao reconectar WiFi.");
      return false;
    }
  }

  HTTPClient http;
  http.begin(SERVER_URL);
  http.addHeader("Content-Type", "application/json");

  // timestamp ISO (opcional): converte millis() para ISO aproximado usando epoch
  // OBS: sem RTC, timestamp será tempo desde boot — ideal é ter RTC ou receber do servidor
  unsigned long ms = millis();
  String ts = String(ms); // o Flask aceita ms desde epoch também (o backend tenta parse)

  String payload = "{";
  payload += "\"grams\": " + String(diferenca, 2) + ",";
  payload += "\"timestamp\": \"" + ts + "\"";
  payload += "}";

  int code = http.POST(payload);
  Serial.printf("HTTP POST code: %d\n", code);
  if (code > 0) {
    String resp = http.getString();
    Serial.println("Resposta servidor: " + resp);
  } else {
    Serial.printf("Erro ao enviar: %s\n", http.errorToString(code).c_str());
  }
  http.end();

  return (code >= 200 && code < 300);
}
