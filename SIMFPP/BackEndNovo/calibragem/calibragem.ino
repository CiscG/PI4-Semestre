#include "HX711.h"

// PINAGEM
#define PIN_DOUT  4
#define PIN_SCK   5

HX711 balanca;

// ALTERE ESTE VALOR APÓS CALIBRAR
float fator = 1.0;

void setup() {
  Serial.begin(115200);
  delay(500);

  balanca.begin(PIN_DOUT, PIN_SCK);
  Serial.println("Remova qualquer peso da balança...");
  delay(3000);

  balanca.set_scale();
  balanca.tare();   // Zera a balança

  Serial.println("Tara concluída!");
  Serial.println("Coloque um peso conhecido na balança...");
}

void loop() {
  long leitura = balanca.read_average(10);

  Serial.print("Leitura RAW: ");
  Serial.println(leitura);

  delay(1000);
}
