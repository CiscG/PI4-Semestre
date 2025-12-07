#include <WiFi.h>
#include <HTTPClient.h>
#include "HX711.h"

// ================= CONFIGURAÇÕES =================

// WIFI
const char* ssid = "Francisco";
const char* password = "vila3540";

// ENDPOINT DO BACKEND
const char* serverName = "http://SEU_IP:3000/api/weight";

// PINOS HX711
#define DOUT  18
#define CLK   19

// FATOR DE CALIBRAÇÃO (ajuste conforme sua balança)
#define FATOR_CALIBRACAO  2280.0

// ================= OBJETOS =================

HX711 balanca;

// ================= VARIÁVEIS =================

bool primeiraLeitura = true;
int ultimoPeso = 0;

// ================= SETUP =================

void setup() {
  Serial.begin(115200);

  // HX711
  balanca.begin(DOUT, CLK);
  balanca.set_scale(FATOR_CALIBRACAO);
  balanca.tare();   // Zera a balança

  // WIFI
  WiFi.begin(ssid, password);
  Serial.print("Conectando no WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi conectado!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

// ================= LOOP =================

void loop() {
  if (WiFi.status() != WL_CONNECTED || !balanca.is_ready()) {
    delay(2000);
    return;
  }

  float pesoFloat = balanca.get_units(10);
  int pesoAtual = (int)pesoFloat;  // SEM casas decimais

  // ===== PRIMEIRA LEITURA =====
  if (primeiraLeitura) {
    ultimoPeso = pesoAtual;
    primeiraLeitura = false;

    Serial.print("Primeiro peso salvo: ");
    Serial.print(ultimoPeso);
    Serial.println(" g");

    delay(10000);
    return;
  }

  // ===== MONITORAMENTO =====
  Serial.print("Valor salvo: ");
  Serial.print(ultimoPeso);
  Serial.println(" g");

  Serial.print("Novo valor: ");
  Serial.print(pesoAtual);
  Serial.println(" g");

  // ===== REGRA PRINCIPAL =====
  if (pesoAtual < ultimoPeso) {
    int diferenca = ultimoPeso - pesoAtual;

    Serial.print("✅ Queda detectada! Diferença enviada: ");
    Serial.print(diferenca);
    Serial.println(" g");

    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");

    String json = "{\"grams\": " + String(diferenca) + "}";

    int httpResponseCode = http.POST(json);

    Serial.print("Resposta servidor: ");
    Serial.println(httpResponseCode);

    http.end();
  } 
  else {
    Serial.println("❌ Peso aumentou ou manteve. NÃO enviado.");
  }

  // ✅ SEMPRE salva o novo valor
  ultimoPeso = pesoAtual;

  delay(10000); // Leituras a cada 10 segundos
}
