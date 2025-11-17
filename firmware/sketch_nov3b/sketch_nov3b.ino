// SLAVE

#include <Wire.h>
#include <SoftPWM.h>

// --- Comandos ---
#define CMD_A2A "A2A"
#define CMD_A2R "A2R"
#define CMD_A2P "A2P"
#define CMD_A3A "A3A"
#define CMD_A3R "A3R"
#define CMD_A3P "A3P"
#define CMD_A4A "A4A"
#define CMD_A4R "A4R"
#define CMD_A4P "A4P"
#define CMD_A5A "A5A"
#define CMD_A5R "A5R"
#define CMD_A5P "A5P"
#define CMD_STATUS "STATUS_REQ"

// --- Pinos Enable ---
const int L_EN[] = {2, 6, 10, A0};
const int R_EN[] = {3, 7, 11, A1};

// --- Pinos PWM ---
const int LPWM[] = {5, 8, 12, A2};
const int RPWM[] = {4, 9, 13, A3};

// Variáveis globais
String ultimoComando = "";
String respostaStatus = "";

// --- Classe Atuador ---
class Atuador {
  public:
    int L_EN, R_EN, LPWM, RPWM, pwm;

    enum Status { AVANCANDO, RETORNANDO, PARADO };
    Status estado;

    Atuador(int l_en, int r_en, int lpwm, int rpwm, int pwmDefault) {
      L_EN = l_en;
      R_EN = r_en;
      LPWM = lpwm;
      RPWM = rpwm;
      pwm = pwmDefault;
      estado = PARADO;

      pinMode(L_EN, OUTPUT);
      pinMode(R_EN, OUTPUT);
      SoftPWMSet(LPWM, 0);
      SoftPWMSet(RPWM, 0);
    }

    void avancar() {
      digitalWrite(L_EN, HIGH);
      digitalWrite(R_EN, HIGH);
      SoftPWMSet(LPWM, pwm);
      SoftPWMSet(RPWM, 0);
      estado = AVANCANDO;
    }

    void retornar() {
      digitalWrite(L_EN, HIGH);
      digitalWrite(R_EN, HIGH);
      SoftPWMSet(LPWM, 0);
      SoftPWMSet(RPWM, pwm);
      estado = RETORNANDO;
    }

    void parar() {
      SoftPWMSet(LPWM, 0);
      SoftPWMSet(RPWM, 0);
      estado = PARADO;
    }
};

// Instâncias
Atuador atuador2(L_EN[0], R_EN[0], LPWM[0], RPWM[0], 100);
Atuador atuador3(L_EN[1], R_EN[1], LPWM[1], RPWM[1], 100);
Atuador atuador4(L_EN[2], R_EN[2], LPWM[2], RPWM[2], 100);
Atuador atuador5(L_EN[3], R_EN[3], LPWM[3], RPWM[3], 100);

void atualizaStatus() {
  respostaStatus = "";
  respostaStatus += "A2:" + String(atuador2.estado) + ",";
  respostaStatus += "A3:" + String(atuador3.estado) + ",";
  respostaStatus += "A4:" + String(atuador4.estado) + ",";
  respostaStatus += "A5:" + String(atuador5.estado);
  Serial.print("Status pronto: ");
  Serial.println(respostaStatus);
}

void recebeDados(int quantidade) {
  ultimoComando = "";

  while (Wire.available()) {
    char c = Wire.read();          
    ultimoComando += c;
  }

  Serial.print("Comando recebido: ");
  Serial.println(ultimoComando);

  // === Executa ação ===
  if (ultimoComando == CMD_A2A) atuador2.avancar();
  else if (ultimoComando == CMD_A2R) atuador2.retornar();
  else if (ultimoComando == CMD_A2P) atuador2.parar();
  else if (ultimoComando == CMD_A3A) atuador3.avancar();
  else if (ultimoComando == CMD_A3R) atuador3.retornar();
  else if (ultimoComando == CMD_A3P) atuador3.parar();
  else if (ultimoComando == CMD_A4A) atuador4.avancar();
  else if (ultimoComando == CMD_A4R) atuador4.retornar();
  else if (ultimoComando == CMD_A4P) atuador4.parar();
  else if (ultimoComando == CMD_A5A) atuador5.avancar();
  else if (ultimoComando == CMD_A5R) atuador5.retornar();
  else if (ultimoComando == CMD_A5P) atuador5.parar();

  delay(150);
  atualizaStatus();
}

void enviaDados() {
  Wire.write(respostaStatus.c_str());
}

void setup() {
  Wire.begin(8); // Endereço do escravo
  Serial.begin(9600);
  SoftPWMBegin();

  Wire.onReceive(recebeDados);
  Wire.onRequest(enviaDados);

  atualizaStatus();
}

void loop() {}
