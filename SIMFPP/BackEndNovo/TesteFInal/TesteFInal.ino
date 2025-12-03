#include "HX711.h"

#define PIN_DOUT  4
#define PIN_SCK   5

#define FATOR_CALIBRACAO  -732.15   // TROQUE PELO SEU VALOR

HX711 balanca;

void setup() {
  Serial.begin(115200);

  balanca.begin(PIN_DOUT, PIN_SCK);
  balanca.set_scale(FATOR_CALIBRACAO);
  balanca.tare();

  Serial.println("Balança pronta.");
}

void loop() {
  float peso = balanca.get_units(5);
  Serial.print("Peso: ");
  Serial.print(peso, 2);
  Serial.println(" g");

  delay(1000);
}
