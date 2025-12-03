#include <WiFi.h>
#include <HTTPClient.h>
#include "HX711.h"
#include <Preferences.h>
#include <time.h>

// ===== CONFIG =====
const char* WIFI_SSID = "SEU_WIFI";
const char* WIFI_PASSWORD = "SUA_SENHA";
const char* SERVER_URL = "http://SEU_IP_DO_SERVIDOR:8000/api/weight";

// HX711
#define PIN_DOUT  4
#define PIN_SCK   5

// BOTÃO DE LEITURA MANUAL
#define PIN_BOTAO 18

// ✅ CALIBRAÇÃO (SUBSTITUIR PELO SEU VALOR REAL DEPOIS)
#define FATOR_CALIBRACAO  SEU_VALOR_AQUI

// VARIAÇÃO MÍNIMA PARA IGNORAR RUÍDO (g)
#define LIMIAR_RUIDO  3.0

// INTERVALO AUTOMÁTICO (ms)
unsigned long intervaloLeitura = 5000;
unsigned long ultimaLeitura = 0;

// OBJETOS
HX711 balanca;
Preferences prefs;

// PESO SALVO
float pesoSalvo = 0.0;

// ================= SETUP =================
void setup() {
  Serial.begin(115200);
  delay(200);

  pinMode(PIN_BOTAO, INPUT_PULLUP);

  // HX711
  balanca.begin(PIN_DOUT, PIN_SCK);
  delay(500);

  if (!balanca.is_ready()) {
    Serial.println("Erro: HX711 não respondeu!");
  } else {
    Serial.println("HX711 pronto.");
    balanca.set_scale(FATOR_CALIBRACAO);
    balanca.tare();
  }

  // MEMÓRIA
  prefs.begin("balanca", false);
  pesoSalvo = prefs.getFloat("peso", 0.0);
  Serial.printf("Peso restaurado da memória: %.2f g\n", pesoSalvo);

  // WIFI
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado!");

  // NTP
  configTime(-3 * 3600, 0, "pool.ntp.org", "time.nist.gov");
  Serial.println("Sincronizando horário...");
  delay(2000);
}

// ================= LOOP =================
void loop() {
  unsigned long agora = millis();

  // ✅ LEITURA AUTOMÁTICA
  if (agora - ultimaLeitura >= intervaloLeitura) {
    ultimaLeitura = agora;
    processarLeitura();
  }

  // ✅ LEITURA MANUAL POR BOTÃO
  if (digitalRead(PIN_BOTAO) == LOW) {
    Serial.println("✅ Botão pressionado -> leitura imediata!");
    processarLeitura();
    delay(500); // debounce
  }
}

// ================= LEITURA PRINCIPAL =================
void processarLeitura() {
  if (!balanca.is_ready()) {
    Serial.println("HX711 não pronto.");
    return;
  }

  float pesoAtual = balanca.get_units(10);

  Serial.println("---------------------------");
  Serial.printf("Peso atual: %.2f g\n", pesoAtual);
  Serial.printf("Peso salvo: %.2f g\n", pesoSalvo);

  // ✅ FILTRO DE RUÍDO
  if (abs(pesoAtual - pesoSalvo) < LIMIAR_RUIDO) {
    Serial.println("Variação ignorada (ruído).");
    return;
  }

  // ✅ AUMENTO DE PESO → só atualiza
  if (pesoAtual > pesoSalvo) {
    Serial.println("Peso aumentou → atualizando base.");
    pesoSalvo = pesoAtual;
    salvarPeso();
    return;
  }

  // ✅ QUEDA DE PESO → ENVIA
  if (pesoAtual < pesoSalvo) {
    float diferenca = pesoSalvo - pesoAtual;
    Serial.printf("Consumo detectado: %.2f g\n", diferenca);

    if (enviarParaServidor(diferenca)) {
      pesoSalvo = pesoAtual;
      salvarPeso();
    } else {
      Serial.println("Falha no envio. Mantendo peso antigo.");
    }
  }
}

// ================= SALVAR NA MEMÓRIA =================
void salvarPeso() {
  prefs.putFloat("peso", pesoSalvo);
  Serial.println("Peso salvo na memória.");
}

// ================= ENVIO HTTP =================
bool enviarParaServidor(float diferenca) {
  if (WiFi.status() != WL_CONNECTED) return false;

  HTTPClient http;
  http.begin(SERVER_URL);
  http.addHeader("Content-Type", "application/json");

  // DATA REAL
  struct tm timeinfo;
  getLocalTime(&timeinfo);
  char timestamp[25];
  strftime(timestamp, 25, "%Y-%m-%d %H:%M:%S", &timeinfo);

  String payload = "{";
  payload += "\"grams\": " + String(diferenca, 2) + ",";
  payload += "\"timestamp\": \"" + String(timestamp) + "\"";
  payload += "}";

  int code = http.POST(payload);
  Serial.printf("HTTP POST code: %d\n", code);

  http.end();
  return (code >= 200 && code < 300);
}
