#include "HX711.h"

#define DOUT 19
#define CLK  18

HX711 scale;

void setup() {
  Serial.begin(115200);
  scale.begin(DOUT, CLK);

  Serial.println("Inicializando HX711...");
  delay(2000);
}

void loop() {
  if (scale.is_ready()) {
    long valor = scale.read();  // leitura CRUA

    Serial.print("Leitura bruta: ");
    Serial.println(valor);
  } else {
    Serial.println("HX711 não pronto!");
  }

  delay(1000);
}
