/**
 * gpiotest.c
 * 28.12.2021
 * D: Kvaavik
 * 
 * Super simple GPIO test program to check all the non-serviced GPIO 
 * on the Raspbery Pi 2 device.
 * 
 * The J8 40 pin header is connected to the BCM2835 SoC General 
 * Purpose IO (GPIO) ports in a particular way.
 * 
 * The wiringPi c-library provide an API for accessing each GPIO through
 * the GPIO pins 32-bit registe, which is available a memory mapped 
 * physical address in the SoC.
 * 
 * This introduces a sort of strange "cross-wiring-section" that will 
 * provide the software-to-hardware relationship.
 * 
 * For instance, the GPIO_4 is exposed on the BCM2835 at Ball Grid Array
 * position RxCy (RowX & ColumnY) and it's control-register is located 
 * at the BCM2835 GPIO base address + 7. This BGA position is then wired
 * to pin 7 of the 40 pin header J8.
 * 
 * The only relevant information needed to use the GPIO_4 is the pin 
 * that represents GPIO_4, in this case pin 7 (be aware of how the pins 
 * are numbered on pin-headers) on the 40 pin header AND that the 
 * register og this GPIO pin is found 7*4 bytes offset from the base 
 * GPIO address
 *                          ==> the physical pin location
 *                          |
 * #define GPIO_4 7  // J8 p7 (Jack 8 pin 7)
 *                |
 *                ==> The register address offset
 * 
 * So, to avoid as much as possible, the confusing "cross-connections"
 * we'll combine/couple the pin location in the 40 pin header and the 
 * offsett register address that control this particular physical pin.  
 * 
 * Offset Addr 7 <===> J8p07
 * ==> 
 * #define J8p07 7    // GPIO_4
 * #define J8p11 0    ∕∕ GPIO_17
 * ... 
 * This particular code implemets a 6-step 3-phase inverter logic, 
 * which is to drive a BLDC motor.
 * 
 * Dependencies:
 * The wiringPi library must be installed (usually part of the Raspbian 
 * OS). Check by: 
 * $ gpio -v 
 * gpio version: 2.50
 * ........
 * ........
 * 
 * Build command:
 * gcc -o gpiotest gpiotest.c -l wiringPi
 * 
 */
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <wiringPi.h>

#define J8p11  0 // GPIO_17
#define J8p12  1 // GPIO_18
#define J8p13  2 // GPIO_27
#define J8p15  3 // GPIO_22
#define J8p16  4 // GPIO_23
#define J8p18  5 // GPIO_24
#define J8p22  6 // GPIO_25
#define J8p07  7 // GPIO_4

#define J8p29 21 // GPIO_5
#define J8p31 22 // GPIO_6
#define J8p33 23 // GPIO_13
#define J8p35 24 // GPIO_19
#define J8p37 25 // GPIO_26
#define J8p32 26 // GPIO_12
#define J8p36 27 // GPIO_16
#define J8p38 28 // GPIO_20
#define J8p40 29 // GPIO_21


static void allLightsOff();
//static void interruptHandler(const int);

static void allLightsOff() {
  digitalWrite(J8p07, LOW);
  digitalWrite(J8p11, LOW);
  digitalWrite(J8p13, LOW);
  digitalWrite(J8p15, LOW);
  digitalWrite(J8p12, LOW);
  digitalWrite(J8p16, LOW);
}
/*
static void interruptHandler(const int signal) {
  allLightsOff();
  exit(0);
}
*/
int main(int argc, char **argv) {
  double interval = 17;
  //signal(SIGINT, interruptHandler);

  if (-1 == wiringPiSetup()) {
    printf("Failed to setup Wiring Pi!\n");
    return 1;
  }
  printf("Setting pin mode\n");
  pinMode(J8p07, OUTPUT); // s1(+)
  pinMode(J8p11, OUTPUT); // s1(-)
  pinMode(J8p13, OUTPUT); // s2(+)
  pinMode(J8p15, OUTPUT); // s2(-)
  pinMode(J8p12, OUTPUT); // s3(+)
  pinMode(J8p16, OUTPUT); // s3(-)
  allLightsOff();
  
  char input[20];
  //char *ptr;
  int len;
  double freq;
  double stepTime;
  
  if (argc > 1) {
    len = snprintf(input, sizeof(input), "%s", argv[1]);
    if (len > sizeof(input)) {
      printf("Input string too long!\n");
    }
    else {
      freq = (double) strtol(input, (char **)NULL, 10);
      printf("Input = %s   len = %d   freq = %f\n", input, len, freq);
      
      stepTime = 1000/(freq*6);
      printf("stepTime = %.6f\n", (float)stepTime);
      interval = stepTime;
    }
  }
     
  while(1) {
    // step#1
    //printf("s1(+) & s3(-)\n");
    digitalWrite(J8p15, LOW);
    digitalWrite(J8p16, HIGH);
    delay(interval);

    // step#2
    //printf("s2(+) & s3(-)\n");
    digitalWrite(J8p07, LOW);    
    digitalWrite(J8p13, HIGH);
    delay(interval);

    // step#3
    //printf("s2(+) & s1(-)\n");
    digitalWrite(J8p16, LOW);
    digitalWrite(J8p11, HIGH);
    delay(interval);

    // step#4
    //printf("s3(+) & s1(-)\n");
    digitalWrite(J8p13, LOW);
    digitalWrite(J8p12, HIGH);
    delay(interval);

    // step#5
    //printf("s3(+) & s2(-)\n");
    digitalWrite(J8p11, LOW);
    digitalWrite(J8p15, HIGH);
    delay(interval);

    // step#6
    //printf("s1(+) & s2(-)\n");
    digitalWrite(J8p12, LOW);
    digitalWrite(J8p07, HIGH);
    delay(interval);
  }

  // Never reached, keeps the compiler happy.
  return 0;
}
