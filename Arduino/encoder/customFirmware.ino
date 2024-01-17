#include <Arduino.h>

#define ENCODER_PIN_A 2 
#define ENCODER_PIN_B 3
#define PPR 374
#define WHEEL_DIAMETER 0.080 // metres

volatile long encoderCount = 0;
float distance = 0;
int lastEncoded = 0;

void setup() {
    Serial.begin(115200);
    pinMode(ENCODER_PIN_A, INPUT);
    pinMode(ENCODER_PIN_B, INPUT);
    // Makes change on either pin trigger an interrupt
    attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_A), encoderISR, CHANGE);
    attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_B), encoderISR, CHANGE);
}

void loop() {
    distance = (encoderCount / (float)PPR) * PI * WHEEL_DIAMETER;
    Serial.print("Distance: ");
    Serial.println(distance);
    delay(1000); // Update every second
}

void encoderISR() {
    int MSB = digitalRead(ENCODER_PIN_A); 
    int LSB = digitalRead(ENCODER_PIN_B); 

    int encoded = (MSB << 1) | LSB; // Combines the two values into one number with a bitwise shift and bitwise OR
    
    int sum  = (lastEncoded << 2) | encoded; // Adds the previous encoder value to the current value to determine direction

    if (sum == 0b1101 || sum == 0b0100 || sum == 0b0010 || sum == 0b1011) encoderCount ++;
    if (sum == 0b1110 || sum == 0b0111 || sum == 0b0001 || sum == 0b1000) encoderCount --;

    lastEncoded = encoded; // Store value for next iteration
}