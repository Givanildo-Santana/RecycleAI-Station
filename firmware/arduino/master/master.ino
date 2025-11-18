#include <Wire.h>
#include <SoftPWM.h>     // Biblioteca instalada por você (SoftPWMSet / SoftPWMPercent)

// === DEFINIÇÕES DOS PINOS ===
#define A2C1 2
#define A2C2 3
#define A3C1 4
#define A3C2 5
#define A4C1 6
#define A4C2 7
#define A5C1 8
#define A5C2 9

// === DEFINIÇÃO DOS PINOS DA ESTEIRA ===
#define RPWM   10
#define LPWM   11
#define R_EN   12
#define L_EN   13

// === COMANDOS ===
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

#define AVANCANDO  0
#define RETORNANDO 1
#define PARADO     2

// === VARIÁVEIS ===
const int pinosChaves[] = {A2C1, A2C2, A3C1, A3C2, A4C1, A4C2, A5C1, A5C2};
const int numPinos = 8;

String comandoSerial = "";
int statusA2 = 2;
int statusA3 = 2;
int statusA4 = 2;
int statusA5 = 2;

// ======================================================
//           CONFIGURAÇÃO DA ESTEIRA - CORRIGIDO
// ======================================================
int pwmInicial = 30;
int pwmFinal   = 120;
int passoPWM   = 5;
int atrasoPWM  = 30;

int lastPWM_R = 0;
int lastPWM_L = 0;

// ======================================================
// Liga a esteira no sentido normal (para a direita)
// ======================================================
void ligarEsteira() {
  Serial.println("[ESTEIRA] Rampa iniciada - Sentido Normal");

  // Habilita a ponte H
  digitalWrite(R_EN, HIGH);
  digitalWrite(L_EN, HIGH);

  // Garante que o lado reverso está desligado
  SoftPWMSet(RPWM, 0);
  lastPWM_R = 0;

  // Rampa no sentido normal (Horário)
  for (int pwm = pwmInicial; pwm <= pwmFinal; pwm += passoPWM) {
    SoftPWMSet(LPWM, pwm);
    lastPWM_L = pwm;
    delay(atrasoPWM);
  }

  Serial.println("[ESTEIRA] Velocidade final atingida.");
}


// ======================================================
// Desliga com rampa suave
// ======================================================
void desligarEsteira() {
  Serial.println("[ESTEIRA] Desaceleração...");

  // Desacelera ambos os sentidos
  for (int pwm = max(lastPWM_R, lastPWM_L); pwm >= 0; pwm -= passoPWM) {
    if (pwm <= lastPWM_R) {
      SoftPWMSet(RPWM, pwm);
      lastPWM_R = pwm;
    }
    if (pwm <= lastPWM_L) {
      SoftPWMSet(LPWM, pwm);
      lastPWM_L = pwm;
    }
    delay(atrasoPWM);
  }

  // Garante que está totalmente parado
  SoftPWMSet(RPWM, 0);
  SoftPWMSet(LPWM, 0);
  lastPWM_R = 0;
  lastPWM_L = 0;

  Serial.println("[ESTEIRA] Motor parado.");
}

// ======================================================
// === Enviar comandos I2C e ler resposta ===
// ======================================================
void enviaComando(String cmd) {
  Wire.beginTransmission(8);
  Wire.write(cmd.c_str());
  Wire.endTransmission();
  delay(10);

  Wire.requestFrom(8, 32);
  String resposta = "";
  while (Wire.available()) {
    char c = Wire.read();
    resposta += c;
  }

  if (resposta.length() > 0) {
    Serial.print("Status recebido: ");
    Serial.println(resposta);
  }

  if (cmd == CMD_STATUS && resposta.length() > 0) {
    parseStatus(resposta);
  }
}

// ======================================================
void parseStatus(String s) {
  int idxA2 = s.indexOf("A2:");
  int idxA3 = s.indexOf("A3:");
  int idxA4 = s.indexOf("A4:");
  int idxA5 = s.indexOf("A5:");

  if (idxA2 >= 0) statusA2 = s.substring(idxA2 + 3, idxA2 + 4).toInt();
  if (idxA3 >= 0) statusA3 = s.substring(idxA3 + 3, idxA3 + 4).toInt();
  if (idxA4 >= 0) statusA4 = s.substring(idxA4 + 3, idxA4 + 4).toInt();
  if (idxA5 >= 0) statusA5 = s.substring(idxA5 + 3, idxA5 + 4).toInt();
}

// ======================================================
// === VERIFICAÇÃO DOS ATUADORES (lógica original) ===
// ======================================================
void verificarAtuador(String nome, int status, int pinoC1, int pinoC2, String cmdRetornar, String cmdParar, int &statusRef) {
  delay(100);
  enviaComando(CMD_STATUS);
  delay(50);

  bool c1 = (digitalRead(pinoC1) == LOW);
  bool c2 = (digitalRead(pinoC2) == LOW);

  if (status == PARADO && !c1 && !c2) {
    Serial.println("⚠️ " + nome + " está parado no meio do curso — retornando à base...");
    enviaComando(cmdRetornar);
    delay(50);
    return;
  }

  if (status == PARADO && c2) {
    Serial.println("⚠️ " + nome + " está parado no topo — retornando à base...");
    enviaComando(cmdRetornar);
    delay(50);
    return;
  }

  if (status == RETORNANDO) {
    if (c1) {
      Serial.println("✅ " + nome + " chegou à base — enviando comando de PARADA...");
      delay(120);
      enviaComando(cmdParar);
      delay(120);
    } else {
      Serial.println("↩️ " + nome + " ainda retornando...");
    }
    return;
  }

  if (status == RETORNANDO && c1) {
    Serial.println("✅ " + nome + " retornou à base — parando...");
    delay(120);
    enviaComando(cmdParar);
    delay(120);
    enviaComando(CMD_STATUS);
    delay(120);
    return;
  }

  if (status == PARADO && c1) {
    Serial.println("🟢 " + nome + " OK — em repouso na base.");
    return;
  }

  if (status == AVANCANDO && c2) {
    Serial.println("🏁 " + nome + " chegou ao topo — enviando comando para RETORNAR...");
    delay(100);
    enviaComando(cmdRetornar);
    delay(100);
    return;
  }

  if (status == AVANCANDO || status == RETORNANDO) return;
}

// ======================================================
String lerComandoSerial() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    return cmd;
  }
  return "";
}

// ======================================================
void setup() {
  Wire.begin();
  Serial.begin(9600);

  for (int i = 0; i < numPinos; i++)
    pinMode(pinosChaves[i], INPUT_PULLUP);

  // === ESTEIRA ===
  pinMode(R_EN, OUTPUT);
  pinMode(L_EN, OUTPUT);
  pinMode(RPWM, OUTPUT);
  pinMode(LPWM, OUTPUT);

  digitalWrite(R_EN, HIGH);
  digitalWrite(L_EN, HIGH);

  // Inicializa SoftPWM
  SoftPWMBegin();
  SoftPWMSet(RPWM, 0);
  SoftPWMSet(LPWM, 0);

  desligarEsteira();
}

// ======================================================
void loop() {

  verificarAtuador("A2", statusA2, A2C1, A2C2, CMD_A2R, CMD_A2P, statusA2);
  verificarAtuador("A3", statusA3, A3C1, A3C2, CMD_A3R, CMD_A3P, statusA3);
  verificarAtuador("A4", statusA4, A4C1, A4C2, CMD_A4R, CMD_A4P, statusA4);
  verificarAtuador("A5", statusA5, A5C1, A5C2, CMD_A5R, CMD_A5P, statusA5);

  String comando = lerComandoSerial();

  if (comando.length() > 0) {

    Serial.print("ARDUINO: Recebi comando -> ");
    Serial.println(comando);

    // =============================
    // ===== BLOCO DE COMANDOS =====
    // =============================

    if (comando.equalsIgnoreCase("Vidro")) {
      Serial.println("Comando: VIDRO → Atuador A2");
      enviaComando(CMD_STATUS);
      delay(30);

      if (statusA2 == 2 && digitalRead(A2C1) == LOW && digitalRead(A2C2) == HIGH) {
        delay(30);
        Serial.println("Esteira Ligada");
        ligarEsteira();
        delay(10000);
        Serial.println("A2 parado na base. Avançando...");
        enviaComando(CMD_A2A);
        enviaComando(CMD_STATUS);
        delay(30);
        desligarEsteira();
      }
    }

    else if (comando.equalsIgnoreCase("Papel")) {
      Serial.println("Esteira Ligada");
      ligarEsteira();
      delay(11000);
      Serial.println("Comando: PAPEL → Atuador A3");
      enviaComando(CMD_A3A);
      delay(6000);
      desligarEsteira();
    }

    else if (comando.equalsIgnoreCase("Plastico")) {
      Serial.println("Comando: PLÁSTICO → Atuador A4");
      enviaComando(CMD_A4A);
    }

    else if (comando.equalsIgnoreCase("Metal")) {
      Serial.println("Comando: METAL → Atuador A5");
      enviaComando(CMD_A5A);
    }

    else if (comando.equalsIgnoreCase("Status")) {
      enviaComando(CMD_STATUS);
    }

    else if (comando.equalsIgnoreCase("Parar")) {
      enviaComando(CMD_A2P);
    }

    else if (comando.equalsIgnoreCase("Retornar")) {
      enviaComando(CMD_A2R);
    }

    else {
      Serial.println("Comando inválido.");
    }

  }

  delay(300);
}