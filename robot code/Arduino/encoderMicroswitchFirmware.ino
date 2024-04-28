#include <Arduino.h>

/*
  Everything seems to lag behind by a couple seconds.
*/


// We communicate with the Arduino at 115200 baud.
#define SERIAL_BAUD 115200
#define FW_VER 1

#define ENCODER_PIN_A 2
#define ENCODER_PIN_B 3
#define MICROSWITCH 7
#define WHEEL_DIAMETER 80 // mm
volatile long encoderCount = 0;
bool microswitch_state = false;
int lastEncoded = 0;

void setup()
{
  Serial.begin(SERIAL_BAUD);
  pinMode(ENCODER_PIN_A, INPUT);
  pinMode(ENCODER_PIN_B, INPUT);
  pinMode(MICROSWITCH, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_A), encoderISR, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_B), encoderISR, CHANGE);
}

int read_pin()
{
  while (!Serial.available())
    ;
  int pin = Serial.read();
  return (int)(pin - 'a');
}

void command_read()
{
  int pin = read_pin();
  // Read from the expected pin.
  int level = digitalRead(pin);
  // Send back the result indicator.
  if (level == HIGH)
  {
    Serial.write('h');
  }
  else
  {
    Serial.write('l');
  }
}

void command_analog_read()
{
  int pin = read_pin();
  int value = analogRead(pin);
  Serial.print(value);
}

void command_write(int level)
{
  int pin = read_pin();
  digitalWrite(pin, level);
}

void command_mode(int mode)
{
  int pin = read_pin();
  pinMode(pin, mode);
}

void loop()
{
  // Fetch all commands that are in the buffer
  while (Serial.available())
  {
    int selected_command = Serial.read();
    // Do something different based on what we got:
    switch (selected_command)
    {
    case 'a':
      command_analog_read();
      break;
    case 'r':
      command_read();
      break;
    case 'l':
      command_write(LOW);
      break;
    case 'h':
      command_write(HIGH);
      break;
    case 'i':
      command_mode(INPUT);
      break;
    case 'o':
      command_mode(OUTPUT);
      break;
    case 'p':
      command_mode(INPUT_PULLUP);
      break;
    case 'v':
      Serial.print("SRcustom:");
      Serial.print(FW_VER);
      break;
    // Custom firmware onwards
    case 'd': // ENABLE ENCODER
      detachInterrupt(digitalPinToInterrupt(MICROSWITCH));
      attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_A), encoderISR, CHANGE);
      attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_B), encoderISR, CHANGE);
      break;
    case 'e': // RETURN ENCODER
      // Makes change on either pin trigger an interrupt
      Serial.println(String(encoderCount));
      break;
    case 'f': // ENABLE MICROSWITCH
      attachInterrupt(digitalPinToInterrupt(MICROSWITCH), microswitchISR, CHANGE);
      detachInterrupt(digitalPinToInterrupt(ENCODER_PIN_A));
      detachInterrupt(digitalPinToInterrupt(ENCODER_PIN_B));
      break;
    case 'g': // RETURN MICROSWITCH
      Serial.println(microswitch_state ? "1" : "0");
      break;
    default:
      // A problem here: we do not know how to handle the command!
      // Just ignore this for now.
      break;
    }
    Serial.print("\n");
  }
}

void encoderISR()
{
  int phaseA = digitalRead(ENCODER_PIN_A);
  int phaseB = digitalRead(ENCODER_PIN_B);

  int encoded = (phaseA << 1) | phaseB; // Combines the two values into one number with a bitwise shift and bitwise OR

  int sum = (lastEncoded << 2) | encoded; // Adds the previous encoder value to the current value to determine direction

  if (sum == 0b0001 || sum == 0b0111 || sum == 0b1110 || sum == 0b1000)
    encoderCount++;

  lastEncoded = encoded; // Store value for next iteration
}

void microswitchISR()
{
    microswitch_state = digitalRead(MICROSWITCH);
}