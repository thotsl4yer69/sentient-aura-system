// Sentient Core - Advanced Arduino Sketch

// Define your peripherals here
struct Peripheral {
  const char* name;
  int pin;
  const char* type; // "led", "sensor", "button", etc.
};

Peripheral peripherals[] = {
  {"built_in_led", 13, "led"},
  {"analog_sensor", A0, "sensor"},
  // Add your own peripherals here, for example:
  // {"red_led", 9, "led"},
  // {"push_button", 2, "button"}
};

const int numPeripherals = sizeof(peripherals) / sizeof(Peripheral);

void setup() {
  Serial.begin(9600);

  for (int i = 0; i < numPeripherals; i++) {
    if (strcmp(peripherals[i].type, "led") == 0) {
      pinMode(peripherals[i].pin, OUTPUT);
    }
    if (strcmp(peripherals[i].type, "button") == 0) {
      pinMode(peripherals[i].pin, INPUT_PULLUP);
    }
  }
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    processCommand(command);
  }
}

void processCommand(String command) {
  int colonIndex = command.indexOf(':');
  String cmd = command;
  String args = "";

  if (colonIndex != -1) {
    cmd = command.substring(0, colonIndex);
    args = command.substring(colonIndex + 1);
  }

  if (cmd == "discover") {
    for (int i = 0; i < numPeripherals; i++) {
      Serial.print("PERIPHERAL:");
      Serial.print(peripherals[i].name);
      Serial.print(":");
      Serial.print(peripherals[i].pin);
      Serial.println(peripherals[i].type);
    }
  } else if (cmd == "read") {
    for (int i = 0; i < numPeripherals; i++) {
      if (strcmp(peripherals[i].name, args.c_str()) == 0) {
        if (strcmp(peripherals[i].type, "sensor") == 0) {
          int sensorValue = analogRead(peripherals[i].pin);
          Serial.print("SENSOR_VALUE:");
          Serial.print(peripherals[i].name);
          Serial.print(":");
          Serial.println(sensorValue);
        } else if (strcmp(peripherals[i].type, "button") == 0) {
          int buttonState = digitalRead(peripherals[i].pin);
          Serial.print("BUTTON_STATE:");
          Serial.print(peripherals[i].name);
          Serial.print(":");
          Serial.println(buttonState);
        }
        return;
      }
    }
    Serial.println("ERROR:Peripheral not found");
  } else if (cmd == "write") {
    int secondColonIndex = args.indexOf(':');
    if (secondColonIndex != -1) {
      String name = args.substring(0, secondColonIndex);
      int value = args.substring(secondColonIndex + 1).toInt();
      for (int i = 0; i < numPeripherals; i++) {
        if (strcmp(peripherals[i].name, name.c_str()) == 0) {
          if (strcmp(peripherals[i].type, "led") == 0) {
            digitalWrite(peripherals[i].pin, value);
            Serial.print("WRITE_OK:");
            Serial.print(name);
            Serial.print(":");
            Serial.println(value);
            return;
          }
        }
      }
    }
    Serial.println("ERROR:Invalid write command");
  }
}
