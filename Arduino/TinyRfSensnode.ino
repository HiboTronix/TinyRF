// **********************************************************************************
// Modified By HiboTronix 2019 https://www.hibotronix.co.uk
// **********************************************************************************
// Copyright Felix Rusu 2018, http://www.LowPowerLab.com/contact
// **********************************************************************************
// License
// **********************************************************************************
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General
// Public License as published by the Free Software
// Foundation; either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will
// be useful, but WITHOUT ANY WARRANTY; without even the
// implied warranty of MERCHANTABILITY or FITNESS FOR A
// PARTICULAR PURPOSE. See the GNU General Public
// License for more details.
//
// Licence can be viewed at
// http://www.gnu.org/licenses/gpl-3.0.txt
//
// Please maintain this license information along with authorship
// and copyright notices in any redistribution of this code
// **********************************************************************************
#include <RFM69.h>         // get it here: https://github.com/lowpowerlab/rfm69
#include <RFM69_ATC.h>     // get it here: https://github.com/lowpowerlab/rfm69
#include <SPI.h>           // included in Arduino IDE (www.arduino.cc)
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <LowPower.h>      // get it here: https://github.com/lowpowerlab/lowpower
//*********************************************************************************************
//************ IMPORTANT SETTINGS - YOU MUST CHANGE/CONFIGURE TO FIT YOUR HARDWARE ************
//*********************************************************************************************
#define GATEWAYID       1 // ID Of Receiving Radio
#define NODEID          2 // This Nodes Unique ID
#define NETWORKID       100  // This Has To Be The Same On All Gateways/Nodes
#define FREQUENCY       RF69_868MHZ  // PCB Antenna Tuned To 868
#define ENCRYPTKEY      "TinyRFSensorNode" // Has To Be The Same 16 Characters/Bytes On All Nodes, Not More, Not Less!
//*********************************************************************************************
#define ENABLE_ATC
#define ATC_RSSI        -75
//*********************************************************************************************
#define SEND_LOOPS      15 // Send Data This Many Sleep Loops (113 Loops Of 8s Cycles = 904s ~ 15 Minutes, 4 Seconds)
period_t sleepTime = SLEEP_4S; // period_t Is An enum Type Defined In The LowPower Library (LowPower.h)
#define LED             9 // Nodes Have A LED On D9
#define BLINK_EN        // Comment Out To Stop Blinking LED On Every Send
#define BME_SCK 13
#define BME_MISO 12
#define BME_MOSI 11
#define BME_CS 3
#define SEALEVELPRESSURE_HPA (1013.25)

RFM69_ATC radio;

char Pstr[10];
char Fstr[10];
char Hstr[10];
double F, P, H;
char buffer[50];
//int txlvl = 0;
unsigned long delayTime;
char input = 0;
byte sendLoops = 0;
byte sendLen;

Adafruit_BME280 bme(BME_CS); // Hardware SPI

void setup(void) {
  //Serial.begin(9600);
  pinMode(LED, OUTPUT);
  radio.initialize(FREQUENCY, NODEID, NETWORKID);
  //radio.encrypt(ENCRYPTKEY);
  radio.enableAutoPower(ATC_RSSI);
  if (!bme.begin()) {
    while (1);  // BME280 Failed To Init, Sit Here As There Is No Point Continuing
  }
  bme.setSampling(Adafruit_BME280::MODE_FORCED,
                  Adafruit_BME280::SAMPLING_X1, // temperature
                  Adafruit_BME280::SAMPLING_X1, // pressure
                  Adafruit_BME280::SAMPLING_X1, // humidity
                  Adafruit_BME280::FILTER_OFF   );
  radio.sendWithRetry(GATEWAYID, "START", 6, 0);
  Blink(LED, 100); Blink(LED, 100); Blink(LED, 100);
  for (uint8_t i = 0; i <= A5; i++) {
    if (i == RF69_SPI_CS) {
      continue;
    }
    pinMode(i, OUTPUT);
    digitalWrite(i, LOW);
  }
}

void loop() {
  if (sendLoops-- <= 0) {  // Send Readings Every SEND_LOOPS
    sendLoops = SEND_LOOPS - 1;
    bme.takeForcedMeasurement(); // Read BME280
    P = bme.readPressure() / 100.0F;
    F = bme.readTemperature();
    H = bme.readHumidity();
    //txlvl = radio._transmitLevel;
    dtostrf(F, 3, 2, Fstr);
    dtostrf(H, 3, 2, Hstr);
    dtostrf(P, 3, 2, Pstr);
    //sprintf(buffer, "T:%s H:%s P:%s", "25", "78", "1234");
    sprintf(buffer, "T:%s H:%s P:%s", Fstr, Hstr, Pstr);
    sendLen = strlen(buffer);
    radio.sendWithRetry(GATEWAYID, buffer, sendLen, 0);
#ifdef BLINK_EN
    Blink(LED, 5);
#endif
  }
  if (radio.receiveDone()) {
    if (radio.ACK_REQUESTED) {
      radio.sendACK();
    }
  }
  radio.sleep();
  LowPower.powerDown(sleepTime, ADC_OFF, BOD_OFF);
  // Wake Up Here
}

void Blink(byte PIN, byte DELAY_MS) {
  pinMode(PIN, OUTPUT);
  digitalWrite(PIN, HIGH);
  delay(DELAY_MS / 2);
  digitalWrite(PIN, LOW);
  delay(DELAY_MS / 2);
}
