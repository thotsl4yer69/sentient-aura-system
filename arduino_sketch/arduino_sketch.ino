// Sentient Core - Arduino Mega 2560 Sensor Controller
// Final Production Configuration - v4.0
// Implements full command protocol for Python daemon communication
//
// Protocol:
//   PING -> PONG
//   GET_PERIPHERALS -> PERIPHERAL:name:pin:type (multiple lines) -> END_OF_LIST
//   discover -> (legacy, same as GET_PERIPHERALS)
//   read:name -> SENSOR_VALUE:name:value (or multi-line for complex sensors)
//   write:name:value -> WRITE_OK:name:value

// ========================================
// LIBRARY INCLUDES
// ========================================

#include <SPI.h>
#include <LedControl.h>
#include <DHT.h>

// ========================================
// PIN DEFINITIONS
// ========================================

// DHT11 Temperature/Humidity Sensor
#define DHT_PIN 2
#define DHT_TYPE DHT11

// HC-SR04 Ultrasonic Distance Sensor
#define ULTRASONIC_TRIG_PIN 9
#define ULTRASONIC_ECHO_PIN 10

// PIR Motion Sensor
#define PIR_PIN 24

// Analog Microphone/Sound Sensor
#define MIC_PIN A3

// Status LED (built-in)
#define STATUS_LED_PIN LED_BUILTIN

// MAX7219 LED Matrix (Hardware SPI)
// Uses hardware SPI pins: MOSI=51, MISO=50, SCK=52
#define LED_MATRIX_CS_PIN 14

// ========================================
// SERIAL CONFIGURATION
// ========================================

#define BAUD_RATE 115200
#define SERIAL_BUFFER_SIZE 128

// ========================================
// PERIPHERAL OBJECTS
// ========================================

// DHT Sensor
DHT dht1(DHT_PIN, DHT_TYPE);

// LED Matrix Controller
// LedControl(dataPin, clkPin, csPin, numDevices)
// For hardware SPI on Mega: DIN=51, CLK=52
LedControl ledMatrix = LedControl(51, 52, LED_MATRIX_CS_PIN, 1);

// ========================================
// PERIPHERAL REGISTRY
// ========================================

struct Peripheral {
  const char* name;
  const char* type;
  int primaryPin;
  bool isInitialized;
};

// Register all peripherals
Peripheral peripherals[] = {
  {"dht1", "sensor", DHT_PIN, false},
  {"ultrasonic1", "sensor", ULTRASONIC_TRIG_PIN, false},
  {"pir1", "sensor", PIR_PIN, false},
  {"mic1", "sensor", MIC_PIN, false},
  {"status_led", "actuator", STATUS_LED_PIN, false},
  {"led_matrix", "actuator", LED_MATRIX_CS_PIN, false}
};

const int NUM_PERIPHERALS = sizeof(peripherals) / sizeof(Peripheral);

// ========================================
// COMMAND BUFFER
// ========================================

char commandBuffer[SERIAL_BUFFER_SIZE];
int bufferIndex = 0;

// ========================================
// SETUP
// ========================================

void setup() {
  Serial.begin(BAUD_RATE);

  // === HEARTBEAT TEST - Proves Arduino is booting ===
  for (int i = 0; i < 15; i++) {
    Serial.println("HEARTBEAT: BOOTING...");
    delay(200);
  }
  // === END HEARTBEAT TEST ===

  // Brief delay for serial stability
  delay(100);

  // Initialize DHT sensor
  dht1.begin();
  setPeripheralInitialized("dht1", true);

  // Initialize HC-SR04 Ultrasonic
  pinMode(ULTRASONIC_TRIG_PIN, OUTPUT);
  pinMode(ULTRASONIC_ECHO_PIN, INPUT);
  digitalWrite(ULTRASONIC_TRIG_PIN, LOW);
  setPeripheralInitialized("ultrasonic1", true);

  // Initialize PIR Motion Sensor
  pinMode(PIR_PIN, INPUT);
  setPeripheralInitialized("pir1", true);

  // Initialize Microphone (analog input - no pinMode needed)
  setPeripheralInitialized("mic1", true);

  // Initialize Status LED
  pinMode(STATUS_LED_PIN, OUTPUT);
  digitalWrite(STATUS_LED_PIN, LOW);
  setPeripheralInitialized("status_led", true);

  // Initialize LED Matrix (Hardware SPI)
  ledMatrix.shutdown(0, false);  // Wake up display
  ledMatrix.setIntensity(0, 8);  // Set brightness (0-15)
  ledMatrix.clearDisplay(0);     // Clear display
  setPeripheralInitialized("led_matrix", true);

  // Send ready signal
  Serial.println("ARDUINO_READY");
}

// ========================================
// MAIN LOOP
// ========================================

void loop() {
  // Process incoming serial commands
  processSerialInput();

  // Small delay to prevent overwhelming the serial buffer
  delay(10);
}

// ========================================
// SERIAL COMMAND PROCESSING
// ========================================

void processSerialInput() {
  while (Serial.available() > 0) {
    char inChar = Serial.read();

    // End of command (newline)
    if (inChar == '\n' || inChar == '\r') {
      if (bufferIndex > 0) {
        commandBuffer[bufferIndex] = '\0'; // Null terminate
        handleCommand(commandBuffer);
        bufferIndex = 0; // Reset buffer
      }
    }
    // Add to buffer
    else if (bufferIndex < SERIAL_BUFFER_SIZE - 1) {
      commandBuffer[bufferIndex++] = inChar;
    }
    // Buffer overflow protection
    else {
      Serial.println("ERROR:BUFFER_OVERFLOW");
      bufferIndex = 0;
    }
  }
}

void handleCommand(char* command) {
  // Trim whitespace
  trimWhitespace(command);

  // Empty command
  if (strlen(command) == 0) {
    return;
  }

  // PING - Handshake test
  if (strcmp(command, "PING") == 0) {
    Serial.println("PONG");
  }

  // GET_PERIPHERALS - List all available peripherals
  else if (strcmp(command, "GET_PERIPHERALS") == 0 || strcmp(command, "discover") == 0) {
    for (int i = 0; i < NUM_PERIPHERALS; i++) {
      Serial.print("PERIPHERAL:");
      Serial.print(peripherals[i].name);
      Serial.print(":");
      Serial.print(peripherals[i].primaryPin);
      Serial.print(":");
      Serial.println(peripherals[i].type);
    }
    Serial.println("END_OF_LIST");
  }

  // READ:name - Read a sensor value
  else if (strncmp(command, "read:", 5) == 0) {
    char* name = command + 5;
    readPeripheral(name);
  }

  // WRITE:name:value - Write to an actuator
  else if (strncmp(command, "write:", 6) == 0) {
    char* rest = command + 6;
    char* name = strtok(rest, ":");
    char* valueStr = strtok(NULL, ":");

    if (name && valueStr) {
      int value = atoi(valueStr);
      writePeripheral(name, value);
    } else {
      Serial.print("ERROR:INVALID_WRITE_SYNTAX:");
      Serial.println(command);
    }
  }

  // Unknown command
  else {
    Serial.print("ERROR:UNKNOWN_COMMAND:");
    Serial.println(command);
  }
}

// ========================================
// PERIPHERAL READ OPERATIONS
// ========================================

void readPeripheral(char* name) {
  // DHT11 Temperature/Humidity Sensor
  if (strcmp(name, "dht1") == 0) {
    float humidity = dht1.readHumidity();
    float temperature = dht1.readTemperature();

    if (isnan(humidity) || isnan(temperature)) {
      Serial.println("ERROR:DHT_READ_FAILED");
      return;
    }

    // Send multi-line response
    Serial.print("SENSOR_VALUE:dht1_temperature:");
    Serial.println(temperature);
    Serial.print("SENSOR_VALUE:dht1_humidity:");
    Serial.println(humidity);
  }

  // HC-SR04 Ultrasonic Distance Sensor
  else if (strcmp(name, "ultrasonic1") == 0) {
    // Trigger pulse
    digitalWrite(ULTRASONIC_TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(ULTRASONIC_TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(ULTRASONIC_TRIG_PIN, LOW);

    // Read echo pulse
    long duration = pulseIn(ULTRASONIC_ECHO_PIN, HIGH, 30000); // 30ms timeout

    if (duration == 0) {
      Serial.println("ERROR:ULTRASONIC_TIMEOUT");
      return;
    }

    // Calculate distance in cm
    float distance = duration * 0.034 / 2;

    Serial.print("SENSOR_VALUE:ultrasonic1:");
    Serial.println(distance);
  }

  // PIR Motion Sensor
  else if (strcmp(name, "pir1") == 0) {
    int motionDetected = digitalRead(PIR_PIN);
    Serial.print("SENSOR_VALUE:pir1:");
    Serial.println(motionDetected);
  }

  // Analog Microphone/Sound Sensor
  else if (strcmp(name, "mic1") == 0) {
    int soundLevel = analogRead(MIC_PIN);
    Serial.print("SENSOR_VALUE:mic1:");
    Serial.println(soundLevel);
  }

  // Status LED (read current state)
  else if (strcmp(name, "status_led") == 0) {
    int ledState = digitalRead(STATUS_LED_PIN);
    Serial.print("SENSOR_VALUE:status_led:");
    Serial.println(ledState);
  }

  // LED Matrix - report status
  else if (strcmp(name, "led_matrix") == 0) {
    Serial.println("SENSOR_VALUE:led_matrix:READY");
  }

  // Peripheral not found
  else {
    Serial.print("ERROR:PERIPHERAL_NOT_FOUND:");
    Serial.println(name);
  }
}

// ========================================
// PERIPHERAL WRITE OPERATIONS
// ========================================

void writePeripheral(char* name, int value) {
  // Status LED
  if (strcmp(name, "status_led") == 0) {
    digitalWrite(STATUS_LED_PIN, value ? HIGH : LOW);
    Serial.print("WRITE_OK:status_led:");
    Serial.println(value);
  }

  // LED Matrix - Pattern control
  // Value 0 = clear, 1 = all on, 2 = smiley, 3 = heart, 4 = alert
  else if (strcmp(name, "led_matrix") == 0) {
    ledMatrix.clearDisplay(0);

    if (value == 0) {
      // Clear display (already done above)
    }
    else if (value == 1) {
      // All LEDs on
      for (int row = 0; row < 8; row++) {
        for (int col = 0; col < 8; col++) {
          ledMatrix.setLed(0, row, col, true);
        }
      }
    }
    else if (value == 2) {
      // Smiley face
      ledMatrix.setLed(0, 2, 2, true);
      ledMatrix.setLed(0, 2, 5, true);
      ledMatrix.setLed(0, 5, 2, true);
      ledMatrix.setLed(0, 6, 3, true);
      ledMatrix.setLed(0, 6, 4, true);
      ledMatrix.setLed(0, 5, 5, true);
    }
    else if (value == 3) {
      // Heart pattern
      ledMatrix.setLed(0, 1, 2, true);
      ledMatrix.setLed(0, 1, 5, true);
      ledMatrix.setLed(0, 2, 1, true);
      ledMatrix.setLed(0, 2, 3, true);
      ledMatrix.setLed(0, 2, 4, true);
      ledMatrix.setLed(0, 2, 6, true);
      ledMatrix.setLed(0, 3, 1, true);
      ledMatrix.setLed(0, 3, 6, true);
      ledMatrix.setLed(0, 4, 2, true);
      ledMatrix.setLed(0, 4, 5, true);
      ledMatrix.setLed(0, 5, 3, true);
      ledMatrix.setLed(0, 5, 4, true);
    }
    else if (value == 4) {
      // Alert pattern (blinking border)
      for (int i = 0; i < 8; i++) {
        ledMatrix.setLed(0, 0, i, true);
        ledMatrix.setLed(0, 7, i, true);
        ledMatrix.setLed(0, i, 0, true);
        ledMatrix.setLed(0, i, 7, true);
      }
    }

    Serial.print("WRITE_OK:led_matrix:");
    Serial.println(value);
  }

  // Cannot write to sensors
  else if (strcmp(name, "dht1") == 0 || strcmp(name, "ultrasonic1") == 0 ||
           strcmp(name, "pir1") == 0 || strcmp(name, "mic1") == 0) {
    Serial.print("ERROR:CANNOT_WRITE_TO_SENSOR:");
    Serial.println(name);
  }

  // Peripheral not found
  else {
    Serial.print("ERROR:PERIPHERAL_NOT_FOUND:");
    Serial.println(name);
  }
}

// ========================================
// UTILITY FUNCTIONS
// ========================================

void trimWhitespace(char* str) {
  // Trim leading whitespace
  char* start = str;
  while (*start && (*start == ' ' || *start == '\t')) {
    start++;
  }

  // Move string to beginning
  if (start != str) {
    int i = 0;
    while (start[i]) {
      str[i] = start[i];
      i++;
    }
    str[i] = '\0';
  }

  // Trim trailing whitespace
  int len = strlen(str);
  while (len > 0 && (str[len-1] == ' ' || str[len-1] == '\t' ||
                     str[len-1] == '\r' || str[len-1] == '\n')) {
    str[--len] = '\0';
  }
}

void setPeripheralInitialized(const char* name, bool initialized) {
  for (int i = 0; i < NUM_PERIPHERALS; i++) {
    if (strcmp(peripherals[i].name, name) == 0) {
      peripherals[i].isInitialized = initialized;
      return;
    }
  }
}
