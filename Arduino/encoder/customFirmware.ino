#include <Arduino.h>

#define ENCODER_PIN_A 2 
#define ENCODER_PIN_B 3
#define CPR 374
#define WHEEL_DIAMETER 0.080

volatile long encoderCount = 0;
float distance = 0;
int lastEncoded = 0;

void setup() {
    Serial.begin(115200);
    pinMode(ENCODER_PIN_A, INPUT);
    pinMode(ENCODER_PIN_B, INPUT);
    attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_A), encoderISR, CHANGE);
    attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_B), encoderISR, CHANGE);
}

void loop() {
    distance = (encoderCount / (float)CPR) * PI * WHEEL_DIAMETER;
    Serial.print("Distance: ");
    Serial.println(distance);
    delay(1000); // Update every second
}

void encoderISR() {
    int MSB = digitalRead(ENCODER_PIN_A); 
    int LSB = digitalRead(ENCODER_PIN_B); 

    int encoded = (MSB << 1) |LSB; //converting the 2 pin value to single number
    
    int sum  = (lastEncoded << 2) | encoded; //adding it to the previous encoded value

    if(sum == 0b1101 || sum == 0b0100 || sum == 0b0010 || sum == 0b1011) encoderCount ++;
    if(sum == 0b1110 || sum == 0b0111 || sum == 0b0001 || sum == 0b1000) encoderCount --;

    lastEncoded = encoded; //store this value for next time
}