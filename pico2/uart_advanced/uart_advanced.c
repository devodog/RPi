/**
 * Copyright (c) 2020 Raspberry Pi (Trading) Ltd.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 * 
 * Author: Dkv
 * Date  : 05FEB25
 * 
 * The Ambient temperature sensing software for use with the Raspberry Pi 
 * Pico 2 hardware.
 * 
 * Using adc2 and uart0 on the Raspberry Pi Pico 2 for capturing analog values
 * for the LM35 temperature sensor from Texas instruments and sending the ADC-
 * values to the UART port as readable text.
 * 
 * As of to day 28.FEB 2025 we'll include some code for PWM, which is to be 
 * managed by the ADC value...
 * 
 * As of to day 6. MAR 2025 the 2 second loop reads the voltage from a 
 * potentiometer at ADC2 and this value is used to calculate the relative 
 * duty cycle for the PWM signal on pin 4 (GPIO2) 
 * 
 * 25. MAR 2025 implemented soft start for the PWM signals, which is to 
 * increase the duty cycle from "zero" to the current potentiometer setting.
 * The duty cycle increase will span over 1.5 seconds. 
 * GPIO 16 and GPIO 17 is assigned PWM operation.
 * 
 * 24.APR 2025 fixed soft start and added max duty cycle to be 60%.a64
 * Also started to implement a user command for disabling the pot-meters
 * for adjusting the brightness of the led lights.
 * 
 */
#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include "pico/stdlib.h"

#include "hardware/uart.h"
#include "hardware/adc.h"
#include "hardware/irq.h"
#include "hardware/gpio.h"
#include "hardware/pwm.h"

#include "appbuild.h"

#define ADC2_ONLY

#define UART_ID uart0
//#define BAUD_RATE 115200
#define BAUD_RATE 9600
#define DATA_BITS 8
#define STOP_BITS 1
#define PARITY    UART_PARITY_NONE

#define ADC_0_FOR_PWM_CHAN_A 0
#define ADC_1_FOR_PWM_CHAN_B 1
#define ADC2_TEMP 2
#define MAX_DEVICE_TEMPERATURE 50 // Max temperature for the device to be used.

#define PWM_PERIOD 10000 // The period of the PWM signal. 10000 = 2ms. (clockdiv = 250.0f)
#define PWM_DC_MAX 60 // The maximum duty cycle for the PWM signal. 60% = 0.6 * 10000 = 6000.

// We are using pins 0 and 1, but see the GPIO function select table in the
// datasheet for information on which other pins can be used.
#define UART_TX_PIN 0
#define UART_RX_PIN 1

#define TRUE 1
#define FALSE 0

#define ACTIVE 1
#define INACTIVE 0
#define ALL_LEDS 3
#define COMPLETED 1



char cmdBuffer[80]; // Making space for the command to be given on the command-line prompt. 
static int chars_rxed = 0;
uint8_t cmdComplete = 0;
const float conversion_factor = 3.3f / (1 << 12);
unsigned int slice_num = 0;
uint8_t potmeter = ACTIVE;

void uart_printf(const char *format, ...) {
    char buffer[256]; // Adjust size as needed
    va_list args;
    va_start(args, format);
    vsnprintf(buffer, sizeof(buffer), format, args);
    va_end(args);
    uart_puts(UART_ID, buffer);
}

void promt() {
    uart_puts(UART_ID, "\r\npico2>");
}

void set_pwm_duty_cycle(int dc, uint8_t pwmChannel) {
    uart_printf("\r\nPWM Duty Cycle for Channel %d, set to: %d %%\r\n", pwmChannel, (int)(dc * (PWM_DC_MAX / 100.0f)));
    
    if (slice_num >= 0) {
            pwm_set_chan_level(slice_num, pwmChannel, dc * PWM_DC_MAX);
    }
    else {
        uart_printf("\r\nNo valid slice number to use!\r\n");
    }
    promt();
}

void softstartLeds() {
    uint16_t adcReading = 0;
    int pwmDC1 = 0, pwmDC2 = 0;
    int dc1 = 0, dc2 = 0;
    int ledStrip_1_Softstart = !COMPLETED, ledStrip_2_Softstart = !COMPLETED;

    adc_select_input(ADC_0_FOR_PWM_CHAN_A);
    adcReading = adc_read();
    uart_printf("ADC0 Raw value: 0x%03x, voltage: %f V\r\n", adcReading, (adcReading * conversion_factor));
    pwmDC1 = (int)(((adcReading * conversion_factor)/3.3)*100); // The fraction between the measured voltage 
                                                                // and the reference voltage represents the 
                                                                // duty cycle for the pwm signal.


    adc_select_input(ADC_1_FOR_PWM_CHAN_B);
    adcReading = adc_read();
    uart_printf("ADC0 Raw value: 0x%03x, voltage: %f V\r\n", adcReading, (adcReading * conversion_factor));
    pwmDC2 = (int)(((adcReading * conversion_factor)/3.3)*100); // The fraction between the measured voltage 


    for (int i = 0; i < 100; i++) {    
        if (dc1 <= pwmDC1) {
            pwm_set_chan_level(slice_num, PWM_CHAN_A, dc1 * PWM_DC_MAX); // ONLY ADC 0 IN USE FOR LED DIM FUNCTION
            dc1++;    
        }
        else {
            ledStrip_1_Softstart = COMPLETED;
        }

        if (dc2 <= pwmDC2) {
            pwm_set_chan_level(slice_num, PWM_CHAN_B, dc2 * PWM_DC_MAX); // ONLY ADC 1 IN USE FOR LED DIM FUNCTION
            dc2++;
        }
        else {
            ledStrip_2_Softstart = COMPLETED;
        }

        if ((ledStrip_1_Softstart == COMPLETED) && (ledStrip_2_Softstart == COMPLETED)) {
            break;
        }
        sleep_ms(50);
    }
}
void getTemperature() {
    uint16_t result = 0;
    adc_select_input(ADC2_TEMP);
    result = adc_read();
    uart_printf("\r\nADC2 temp: %.1f C°\r\n", ((result * conversion_factor)-0.02)*100); 
}

int8_t checkTemp() {
    // Check for device is overheated.
    uint16_t result = 0;
    adc_select_input(ADC2_TEMP);
    result = adc_read();
    if (((result * conversion_factor)-0.02)*100 > MAX_DEVICE_TEMPERATURE) {
        return 1; // Device is overheated.
        uart_printf("\r\nDevice temperature is overheated: %f.1 C°\r\n", ((result * conversion_factor)-0.02)*100); 
    }
    else {
        return 0; // Device is not overheated.
    }
}

void execCmd(char* cmd) {
    uint16_t result = 0;
    int dc = 0;
    
    if (strncmp(cmdBuffer, "led1", 4) == 0) {        
        adc_select_input(ADC_0_FOR_PWM_CHAN_A); // ...for the pwm-signal
        result = adc_read();
        dc = (int)(((result * conversion_factor)/3.3)*100);
        uart_printf("\r\nADC1 (LED1) DutyCycle: %d %%\r\n", dc);
    }
    
    if (strncmp(cmdBuffer, "led2", 4) == 0) {
        adc_select_input(ADC_1_FOR_PWM_CHAN_B); // ...for the pwm-signal
        result = adc_read();
        dc = (int)(((result * conversion_factor)/3.3)*100);
        uart_printf("\r\nADC1 (LED2) DutyCycle: %d %%\r\n", dc);
    }

    if (strncmp(cmdBuffer, "dc", 2) == 0) {
        // Get the value from the user command.
        dc = (int)strtoul(&cmdBuffer[4], NULL, 10); // Convert the string to an integer.
        if (dc > 100) {
            dc = 100;
        }
        if (cmdBuffer[2] == '1') {
            set_pwm_duty_cycle(dc, PWM_CHAN_A);
        }
        else if (cmdBuffer[2] == '2') {
            set_pwm_duty_cycle(dc, PWM_CHAN_B);
        }
        else {
            uart_puts(UART_ID, "\r\nInvalid command!\r\n");
        }
    }

    if (strncmp(cmdBuffer, "temp", 4) == 0) {
        getTemperature(); // Get the temperature reading from the LM35 sensor.
    }

    if (strncmp(cmdBuffer, "pot", 3) == 0) {
        if (strncmp(&cmdBuffer[4], "off", 3) == 0) {
            potmeter = INACTIVE;
            uart_printf("\r\nPotmeter OFF\r\n");
        }
        else if (strncmp(&cmdBuffer[4], "on", 2) == 0) {
            potmeter = ACTIVE;
            uart_printf("\r\nPotmeter ON\r\n");
            // Soft start until brightness setting reached.
            softstartLeds(); // Soft start the LED Strip 1.
         }
    }

    chars_rxed = 0;
    memset(&cmdBuffer[0], 0, 80); // Clearing the command buffer...
    cmdComplete = FALSE;
    promt();
}



// RX interrupt handler - will trigger for each character received on the rx-uart line.
void on_uart_rx() {
    while (uart_is_readable(UART_ID)) {
        uint8_t ch = uart_getc(UART_ID);
        
        // We'll store the received character in the cmdBuffer and return the received character as an echo to the command-line prompt.?
        if (uart_is_writable(UART_ID)) {
            if (ch == 0xd) {
                if ((chars_rxed > 0) && (cmdComplete == FALSE)) {
                     cmdComplete = TRUE;
                     //uart_puts(UART_ID, "\r\n");
                     execCmd(&cmdBuffer[0]);
                }
                else {
                    promt();
                }                
            }
            else {
                cmdBuffer[chars_rxed] = ch;
                uart_putc(UART_ID, ch);
                chars_rxed++;
            }
        }        
    }
}


void init_pwm_for_leds() {
        gpio_set_function(16, GPIO_FUNC_PWM);
        gpio_set_function(17, GPIO_FUNC_PWM);

        slice_num = pwm_gpio_to_slice_num(16);
        //uart_printf("\r\nSlice Number set to: %d \r\n", slice_num);
        pwm_set_clkdiv(slice_num, 250.0f); // Set the clock divider to 250.0 - 150 Mhz / 250 = 600 KHz.
        pwm_set_wrap(slice_num, PWM_PERIOD); // Set the wrap value for the PWM slice. 600 KHz / 10000 = 60 Hz.
        pwm_set_chan_level(slice_num, PWM_CHAN_A, 0); // Set the initial duty cycle to 0.
        pwm_set_chan_level(slice_num, PWM_CHAN_B, 0); // Set the initial duty cycle to 0.
        pwm_set_enabled(slice_num, true); // Disable the PWM slice.
    }


int main() {
    uint16_t result = 0;
    // Set up our UART with a basic baud rate.
    uart_init(UART_ID, 9600);

    // Set the TX and RX pins by using the function select on the GPIO
    // Set datasheet for more information on function select
    gpio_set_function(UART_TX_PIN, UART_FUNCSEL_NUM(UART_ID, UART_TX_PIN));
    gpio_set_function(UART_RX_PIN, UART_FUNCSEL_NUM(UART_ID, UART_RX_PIN));

    // Actually, we want a different speed
    // The call will return the actual baud rate selected, which will be as close as
    // possible to that requested
    int __unused actual = uart_set_baudrate(UART_ID, BAUD_RATE);

    // Set UART flow control CTS/RTS, we don't want these, so turn them off
    uart_set_hw_flow(UART_ID, false, false);

    // Set our data format
    uart_set_format(UART_ID, DATA_BITS, STOP_BITS, PARITY);

    // Turn off FIFO's - we want to do this character by character
    uart_set_fifo_enabled(UART_ID, false);

    // Set up a RX interrupt
    // We need to set up the handler first
    // Select correct interrupt for the UART we are using
    int UART_IRQ = UART_ID == uart0 ? UART0_IRQ : UART1_IRQ;

    // And set up and enable the interrupt handlers
    irq_set_exclusive_handler(UART_IRQ, on_uart_rx);
    irq_set_enabled(UART_IRQ, true);

    // Now enable the UART to send interrupts - RX only
    uart_set_irq_enables(UART_ID, true, false);

    // OK, all set up.
    // Lets send a basic string out, and then run a loop and wait for RX interrupts
    // The handler will count them, but also reflect the incoming data back with a slight change!
    uart_printf("\r\nRaspberry Pi Pico 2 LED-Strip Driver, version 1.0 APR2025 build: %d\r\n", BUILD);
    uart_puts(UART_ID, "--------------------------------------------------------- \r\n");
    adc_init();
    // Make sure GPIO is high-impedance, no pullups etc
    adc_gpio_init(28); // ADC2 temperature measurements

    adc_gpio_init(27); // ADC1
    adc_gpio_init(26); // ADC0 

    // Soft start until brightness setting reached.
    init_pwm_for_leds(); // Initialize the PWM for the LEDs.
    softstartLeds(); // Soft start the LED Strips.
    
    getTemperature(); // Get the temperature from the LM35 sensor.

    int pwmUpdate = 0, pwm0 = 0, pwm1 = 0;
    int hy = 3; // Hysteresis
    int loopCounter = 0;

    while (1) {
        //tight_loop_contents();       
        if (potmeter == ACTIVE) { 
            // Check if the device is overheated.
            if (checkTemp() == 1) {
                 set_pwm_duty_cycle(0, PWM_CHAN_A); // for PWM_CHAN_A
                set_pwm_duty_cycle(0, PWM_CHAN_B); // for PWM_CHAN_B
                uart_puts(UART_ID, "\r\nPWM signals disabled!\r\n");
                potmeter = INACTIVE; // Disable the potmeter.
                uart_puts(UART_ID, "\r\nPotmeter disabled!\r\n");
                uart_puts(UART_ID, "\r\nPlease check the device!\r\n");
                promt();
                break; // Exit the loop if the device is overheated.
            }

            adc_select_input(ADC_0_FOR_PWM_CHAN_A); // ...for the pwm-signal
            result = adc_read();
            //uart_printf("ADC2 Raw value: 0x%03x, voltage: %f V\r\n", result, result * conversion_factor);
            pwmUpdate = (int)(((result * conversion_factor)/3.3)*100); // The fraction between the measured voltage and the reference voltage represents the duty cycle for the pwm signal.  
            
            if ((pwmUpdate >= (pwm0+hy)) || (pwmUpdate <= (pwm0-hy))) {
                uart_printf("\r\nPWM_0 Duty Cycle update: Old = %d%%, New = %d%%", pwm0, pwmUpdate);
                pwm0 = pwmUpdate;
                set_pwm_duty_cycle(pwm0, PWM_CHAN_A); // for PWM_CHAN_A
            }

            adc_select_input(ADC_1_FOR_PWM_CHAN_B); // ...for the pwm-signal
            result = adc_read();
            //uart_printf("ADC2 Raw value: 0x%03x, voltage: %f V\r\n", result, result * conversion_factor);
            pwmUpdate = (int)(((result * conversion_factor)/3.3)*100);
            
            if ((pwmUpdate >= (pwm1+hy)) || (pwmUpdate <= (pwm1-hy))) {
                uart_printf("\r\nPWM_1 Duty Cycle update: Old = %d%%, New = %d%%", pwm1, pwmUpdate);
                pwm1 = pwmUpdate;
                set_pwm_duty_cycle(pwm1, PWM_CHAN_B); // for PWM_CHAN_B
            }
        }
        // Checking the input every 100 ms.
        sleep_ms(100);
        if (loopCounter >= 1200) { // 1200 * 100 ms = 120 seconds = 2 minutes.
            loopCounter = 0;
            getTemperature(); // Get the temperature from the LM35 sensor.
        }
        loopCounter++;
    }
}
