#include <Arduino.h>

// We communicate with the Arduino at 115200 baud.
#define SERIAL_BAUD 115200
#define FW_VER 1

#define ENCODER_PIN_A 2
#define ENCODER_PIN_B 3
float distance = 0;

void setup()
{
  Serial.begin(SERIAL_BAUD);
  pinMode(ENCODER_PIN_A, INPUT);
  pinMode(ENCODER_PIN_B, INPUT);

  // Makes change on either pin trigger an interrupt
  attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_A), encoderISP, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_B), encoderISP, CHANGE);
}

int read_pin()
{
  while (!Serial.available());
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
    case 'e':
      Serial.write(distance);
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

  if (sum == 0b1101 || sum == 0b0100 || sum == 0b0010 || sum == 0b1011)
    encoderCount++;
  if (sum == 0b1110 || sum == 0b0111 || sum == 0b0001 || sum == 0b1000)
    encoderCount--;

  lastEncoded = encoded; // Store value for next iteration

  distance = (encoderCount / (float)CPR) * PI * WHEEL_DIAMETER; // Finds distance travelled based on ratio to circumference of wheel
}