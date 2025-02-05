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
 */
#include <stdio.h>
#include <stdarg.h>
#include "pico/stdlib.h"
#include "string.h"

#include "hardware/uart.h"
#include "hardware/adc.h"
#include "hardware/irq.h"
#include "hardware/gpio.h"


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
    // Just printing the command given...
    uart_puts(UART_ID, "\r\nCommand received: ");
    uart_puts(UART_ID, cmd);
    uart_puts(UART_ID, "\r\n");
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
                     //execCmd(&cmdBuffer[0]);
                }
                else {
                    uart_puts(UART_ID, "\r\n");
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

int main() {
    // Set up our UART with a basic baud rate.
    uart_init(UART_ID, 2400);

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
    uart_puts(UART_ID, "\nHello, uart interrupts\r\n");
    promt();

    stdio_init_all();
    uart_puts(UART_ID, "ADC Example, measuring GPIO28\r\n");

    adc_init();

    // Make sure GPIO is high-impedance, no pullups etc
    adc_gpio_init(28);
    // Select ADC input 0 (GPIO26)
    adc_select_input(2);

    while (1) {
        // 12-bit conversion, assume max value == ADC_VREF == 3.3 V
        const float conversion_factor = 3.3f / (1 << 12);
        uint16_t result = adc_read();
        uart_printf("Raw value: 0x%03x, voltage: %f V\r\n", result, result * conversion_factor);
        
        sleep_ms(1500);
        
        //tight_loop_contents();
        /**
        if (cmdComplete == TRUE) {
            execCmd (&cmdBuffer[0]);
        }
        else {
            sleep_ms(100);
        }
        */
    }
}

/// \end:uart_advanced[]
