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


/// \tag::uart_advanced[]

#define UART_ID uart0
#define BAUD_RATE 115200
#define DATA_BITS 8
#define STOP_BITS 1
#define PARITY    UART_PARITY_NONE

// We are using pins 0 and 1, but see the GPIO function select table in the
// datasheet for information on which other pins can be used.
#define UART_TX_PIN 0
#define UART_RX_PIN 1

#define TRUE 1
#define FALSE 0

char cmdBuffer[80]; // Making space for the command to be given on the command-line prompt. 
static int chars_rxed = 0;
uint8_t cmdComplete = 0;
const float conversion_factor = 3.3f / (1 << 12);
unsigned int slice_num = 0;

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

void execCmd(char* cmd) {
    uint16_t result = 0;
    int dc = 0;
    // Just printing the command given...
#ifdef COMMAND_TEST
    uart_puts(UART_ID, "\r\nCommand received: ");
    uart_puts(UART_ID, cmd);
    uart_puts(UART_ID, "\r\n");
#else    
    if (strncmp(cmdBuffer, "led1", 4) == 0) {        
        adc_select_input(1); // ...for the pwm-signal
        result = adc_read();
        dc = (int)(((result * conversion_factor)/3.3)*100);
        uart_printf("\r\nADC1 (LED1) DutyCycle: %d %%\r\n", dc);
    }
    
    if (strncmp(cmdBuffer, "led2", 4) == 0) {
        adc_select_input(2); // ...for the pwm-signal
        result = adc_read();
        dc = (int)(((result * conversion_factor)/3.3)*100);
        uart_printf("\r\nADC1 (LED2) DutyCycle: %d %%\r\n", dc);
    }

    if (strncmp(cmdBuffer, "temp", 4) == 0) {
        adc_select_input(0);
        result = adc_read();
        uart_printf("\r\nADC0 temp: %f C°\r\n", ((result * conversion_factor)-0.02)*100);         
    }
#endif

    chars_rxed = 0;
    memset(&cmdBuffer[0], 0, 80); // Clearing the command buffer...
    cmdComplete = FALSE;
    promt();
}


void set_pwm_duty_cycle(int dc, uint8_t pwmChannel) {
    uart_printf("\r\nPWM Duty Cycle set to: %d %%\r\n", dc);
    if (slice_num >= 0) {
        pwm_set_chan_level(slice_num, pwmChannel, dc*100);      // 25% duty cycle
        //pwm_set_chan_level(slice_num, PWM_CHAN_A, dc*10);    
    }
    else {
        //uart_printf("\r\nPWM NOT SET\r\n");
    }
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

// Will need some kind of interrupt to update/adjust the pwm duty cycle - or not...

void pwmLed() {
    // pwm_set_clkdiv(f)
#ifdef ON_BREADBOARD
    gpio_set_function(2, GPIO_FUNC_PWM);
    gpio_set_function(3, GPIO_FUNC_PWM);
    
    slice_num = pwm_gpio_to_slice_num(2);
#else
    gpio_set_function(16, GPIO_FUNC_PWM);
    gpio_set_function(17, GPIO_FUNC_PWM);

    slice_num = pwm_gpio_to_slice_num(16);
#endif

    uart_printf("\r\nSlice Number set to: %d \r\n", slice_num);
    pwm_set_wrap(slice_num, 10000);
    //
    uint16_t adcReading = 0;
    int pwmDC1 = 0, pwmDC2 = 0;
    int deltaDC1 = 0, deltaDC2 = 0;
    
    /*** CURRENTLY THERE IS ONLY ONE POTENTIOMETER CONNECTED TO ADC2 = GPIO
    adc_select_input(1); // ...for the pwm-signal
    adcReading = adc_read();
    //uart_printf("ADC2 Raw value: 0x%03x, voltage: %f V\r\n", result, result * conversion_factor);
    pwmLED1 = (int)(((adcReading * conversion_factor)/3.3)*100);
    delta1 = pwmLED1/10;
    ***/
    adc_select_input(2); // ...for the pwm-signal
    adcReading = adc_read();
    uart_printf("Initial Light Setting: %d%%\r\n", ((adcReading * conversion_factor)/3.3)*100);
    pwmDC2 = (int)(((adcReading * conversion_factor)/3.3)*100);
    deltaDC2 = pwmDC2*10;   // The actual duty cycle in cpu clock cycles is 100 times the duty cycle persentage.
                            // pwmDC2 * 100 / 10 for each interval change to implement soft start lighting.
    
    uart_puts(UART_ID, "\r\nSoft starting.\r\n");
    uint8_t lightON = 0;
    for (int i = 0; i < 10; i++) {    
        pwm_set_chan_level(slice_num, PWM_CHAN_A, deltaDC2);      // ONLY ADC 2 IN USE FOR LED DIM FUNCTION
        pwm_set_chan_level(slice_num, PWM_CHAN_B, deltaDC2);
        deltaDC2 += deltaDC2;
        //set_pwm_duty_cycle(delta1, 0);
        //set_pwm_duty_cycle(delta2, 1);
        
        if (lightON == 0) {
            pwm_set_enabled(slice_num, true);
            lightON = 1;
        }
        sleep_ms(150);
    }
    /*
    pwm_set_chan_level(slice_num, PWM_CHAN_A, 5000);      // 50% duty cycle
    pwm_set_chan_level(slice_num, PWM_CHAN_B, 5000);
    pwm_set_enabled(slice_num, true);
    */
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
    uart_puts(UART_ID, "\r\nHello, uart interrupts\r\n");
    //promt();

    //stdio_init_all();
    uart_puts(UART_ID, "\r\nADC Example, measuring GPIO28\r\n");

    adc_init();

    // Make sure GPIO is high-impedance, no pullups etc
    adc_gpio_init(28);
    //adc_gpio_init(27);
    adc_gpio_init(26);

    // Soft start until brightness setting reached.
    pwmLed();
    int pwmUpdate = 0, pwm = 0;
    uart_puts(UART_ID, "\r\nCompleted.\r\n");
    while (1) {
        //tight_loop_contents();       
        sleep_ms(200);
        //uart_puts(UART_ID, "\r\nIn loop\r\n");
        //for (int i=1; i<3; i++) {
            adc_select_input(2); // ...for the pwm-signal
            result = adc_read();
            //uart_printf("ADC2 Raw value: 0x%03x, voltage: %f V\r\n", result, result * conversion_factor);
            pwmUpdate = (int)(((result * conversion_factor)/3.3)*100);
            
            if ((pwmUpdate >= (pwm+2)) || (pwmUpdate <= (pwm-2))) {
                uart_printf("\r\nPWM Duty Cycle update: Old = %d%%, New = %d%%", pwm, pwmUpdate);
                pwm = pwmUpdate;
                set_pwm_duty_cycle(pwm, 0);
                set_pwm_duty_cycle((100-pwm), 1);
            }
       // }
    }
}

/// \end:uart_advanced[]
