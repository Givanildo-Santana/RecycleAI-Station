// MASTER

#include <Wire.h>

// === DEFINIÇÕES DOS PINOS ===
#define A2C1 2
#define A2C2 3
#define A3C1 4
#define A3C2 5
#define A4C1 6
#define A4C2 7
#define A5C1 8
#define A5C2 9

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

// === Função para enviar comandos e ler resposta ===
void enviaComando(String cmd) {
  Wire.beginTransmission(8); // Endereço do escravo
  Wire.write(cmd.c_str());
  Wire.endTransmission();
  delay(10); // pequeno atraso para o escravo processar

  // Solicita resposta (até 32 bytes)
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

  // --- Atualiza variáveis de status ---
  if (cmd == CMD_STATUS && resposta.length() > 0) {
    parseStatus(resposta);
  }
}

void parseStatus(String s) {
  // Exemplo: "A2:1,A3:2,A4:0,A5:2"
  int idxA2 = s.indexOf("A2:");
  int idxA3 = s.indexOf("A3:");
  int idxA4 = s.indexOf("A4:");
  int idxA5 = s.indexOf("A5:");

  if (idxA2 >= 0) statusA2 = s.substring(idxA2 + 3, idxA2 + 4).toInt();
  if (idxA3 >= 0) statusA3 = s.substring(idxA3 + 3, idxA3 + 4).toInt();
  if (idxA4 >= 0) statusA4 = s.substring(idxA4 + 3, idxA4 + 4).toInt();
  if (idxA5 >= 0) statusA5 = s.substring(idxA5 + 3, idxA5 + 4).toInt();
}

// === Função de verificação individual de atuador ===
void verificarAtuador(String nome, int status, int pinoC1, int pinoC2, String cmdRetornar, String cmdParar, int &statusRef) {
  // 1️⃣ Solicita status atualizado ao slave
  delay(100);
  enviaComando(CMD_STATUS);
  delay(50);

  // 2️⃣ Lê o estado das chaves
  bool c1 = (digitalRead(pinoC1) == LOW);  // Chave inferior (base)
  bool c2 = (digitalRead(pinoC2) == LOW);  // Chave superior (topo)

  // ===========================================================
  // CASO 1: Atuador "perdido" — parado mas nenhuma chave acionada
  // ===========================================================
  if (status == PARADO && !c1 && !c2) {
    Serial.println("⚠️ " + nome + " está parado no meio do curso — retornando à base...");
    enviaComando(cmdRetornar);
    delay(50);
    return;
  }

  // ===========================================================
  // CASO 2: Atuador parado com chave superior pressionada
  // (significa que parou no topo — deve retornar também)
  // ===========================================================
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
    // Apenas monitoramento, não reenvia o comando
    Serial.println("↩️ " + nome + " ainda retornando...");
  }
  return;
}
  // ===========================================================
  // CASO 3: Atuador retornando e chegou à base
  // ===========================================================
  if (status == RETORNANDO && c1) {
  Serial.println("✅ " + nome + " retornou à base — parando...");

  // Aguarda o barramento I2C ficar livre antes de enviar
  delay(120);
  enviaComando(cmdParar);
  delay(120);   // tempo mínimo para escravo processar

  // Confirma se o status realmente mudou
  enviaComando(CMD_STATUS);
  Serial.println("🔁 Aguardando confirmação de parada...");
  delay(120);

  return;
}

  // ===========================================================
  // CASO 4: Atuador já parado na base (tudo certo)
  // ===========================================================
  if (status == PARADO && c1) {
    Serial.println("🟢 " + nome + " OK — em repouso na base.");
    return;
  }

  // ===========================================================
  // CASO 5: Atuador em movimento normal — nenhuma ação necessária
  // ===========================================================
if (status == AVANCANDO && c2) {
  Serial.println("🏁 " + nome + " chegou ao topo — enviando comando para RETORNAR...");
  
  // Evita flood de comandos — só envia uma vez
  delay(100);
  enviaComando(cmdRetornar);
  delay(100);

  return;
}

  if (status == AVANCANDO || status == RETORNANDO) {
    // Apenas monitora
    return;
  }
}

void setup() {
  Wire.begin();  // Mestre
  Serial.begin(9600);

  for (int i = 0; i < numPinos; i++) {
    pinMode(pinosChaves[i], INPUT_PULLUP);
  }

  Serial.println("Mestre iniciado. Digite um comando (Vidro, Papel, Plastico, Metal):");
}

void loop() {
  // --- Solicita e verifica individualmente cada atuador ---
verificarAtuador("A2", statusA2, A2C1, A2C2, CMD_A2R, CMD_A2P, statusA2);
verificarAtuador("A3", statusA3, A3C1, A3C2, CMD_A3R, CMD_A3P, statusA3);
verificarAtuador("A4", statusA4, A4C1, A4C2, CMD_A4R, CMD_A4P, statusA4);
verificarAtuador("A5", statusA5, A5C1, A5C2, CMD_A5R, CMD_A5P, statusA5);



  // --- Lê comandos do Serial Monitor ---
  if (Serial.available() > 0) {
    comandoSerial = Serial.readStringUntil('\n');
    comandoSerial.trim();

    if (comandoSerial.equalsIgnoreCase("Vidro")) {
      Serial.println("Comando: VIDRO → Atuador A2");
      enviaComando(CMD_STATUS);
      delay(30);

      if (statusA2 == 2 && digitalRead(A2C1) == LOW && digitalRead(A2C2) == HIGH) {
        Serial.println("A2 parado na base. Subindo...");
        enviaComando(CMD_A2A);
        delay(30);
        enviaComando(CMD_STATUS);
      }

    } else if (comandoSerial.equalsIgnoreCase("Papel")) {
      Serial.println("Comando: PAPEL → Atuador A3");
      enviaComando(CMD_A3A);

    } else if (comandoSerial.equalsIgnoreCase("Plastico")) {
      Serial.println("Comando: PLÁSTICO → Atuador A4");
      enviaComando(CMD_A4A);

    } else if (comandoSerial.equalsIgnoreCase("Metal")) {
      Serial.println("Comando: METAL → Atuador A5");
      enviaComando(CMD_A5A);

    } else if (comandoSerial.equalsIgnoreCase("Status")) {
      enviaComando(CMD_STATUS);

    } else if (comandoSerial.equalsIgnoreCase("Parar")) {
      enviaComando(CMD_A2P);

    } else if (comandoSerial.equalsIgnoreCase("Retornar")) {
      enviaComando(CMD_A2R);

    } else {
      Serial.println("Comando inválido.");
    }
  }

  delay(300);
}
