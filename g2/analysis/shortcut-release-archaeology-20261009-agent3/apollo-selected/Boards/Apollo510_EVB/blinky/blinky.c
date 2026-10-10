//*****************************************************************************
//
//! @file blinky.c
//!
//! @brief Simple blinky example for the Apollo510 EVB.
//!
//! This example runs various patterns on the EVB LEDs and sleeps in between
//! the pattern updates.
//!
//! This example is provided only as a simple demonstration using CMSIS
//! register definitions as provided in apollo510.h. This example should
//! not be considered as a project starting point.
//! Please refer to the latest Ambiq SDK for example projects that take full
//! advantage of various hardware and software optimizations for achieving
//! low power and high performance.
//
//*****************************************************************************

//*****************************************************************************
//
// Copyright (c) 2025, Ambiq Micro, Inc.
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:
//
// 1. Redistributions of source code must retain the above copyright notice,
// this list of conditions and the following disclaimer.
//
// 2. Redistributions in binary form must reproduce the above copyright
// notice, this list of conditions and the following disclaimer in the
// documentation and/or other materials provided with the distribution.
//
// 3. Neither the name of the copyright holder nor the names of its
// contributors may be used to endorse or promote products derived from this
// software without specific prior written permission.
//
// Third party software included in this distribution is subject to the
// additional license terms as defined in the /docs/licenses directory.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
// ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
// SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
// INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
// CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
// ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
// POSSIBILITY OF SUCH DAMAGE.
//
// This is part of Ambiq CMSIS pack (initially v1.5.1).
//
//*****************************************************************************


#include <stdint.h>
#include <stdbool.h>
#include "apollo510.h"
#include <core_cm55.h>


//*****************************************************************************
//
// Define LEDs, mapping them to their respective GPIO numbers.
//
//*****************************************************************************
//
// The Apollo510 EVB (c2025) uses the following LEDs:
//
#define EVB_NUMLEDS     3
#define EVB_LED0        165
#define EVB_LED1        89
#define EVB_LED2        92

//
// Apollo510 maximum number of GPIOs
//
#define AM_HAL_PIN_TOTAL_GPIOS  (224)


//*****************************************************************************
//
// Globals
//
//*****************************************************************************
//
// Software timer updated by ISR.
//
volatile uint32_t ui32SoftwareCounter = 0;

//*****************************************************************************
//
// Constant data
//
//*****************************************************************************
//
// Keep the LED pattern array in non-volatile instead of RAM.
//
static const uint8_t led_pattern[64] =
{
    //
    // Binary count up
    //
      0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15,
#if EVB_NUMLEDS >= 4
     16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
#endif

    //
    // Rotate left pattern
    //
#if EVB_NUMLEDS == 3
    0x00, 0x01, 0x02, 0x04, 0x00, 0x01, 0x02, 0x04,
    0x00, 0x01, 0x02, 0x04, 0x00, 0x01, 0x02, 0x04,
#elif EVB_NUMLEDS == 4
    0x00, 0x01, 0x02, 0x04, 0x08, 0x00, 0x01, 0x02, 0x04, 0x08, 0x00,
#elif EVB_NUMLEDS >= 5
    0x01, 0x02, 0x04, 0x08, 0x10, 0x01, 0x02, 0x04, 0x08, 0x10, 0x00,
#endif

    //
    // Rotate right pattern
    //
#if EVB_NUMLEDS == 3
    0x00, 0x04, 0x02, 0x01, 0x00, 0x04, 0x02, 0x01,
    0x00, 0x04, 0x02, 0x01, 0x00, 0x04, 0x02, 0x01,
#elif EVB_NUMLEDS == 4
    0x08, 0x04, 0x02, 0x01, 0x00, 0x08, 0x04, 0x02, 0x01, 0x00, 0x08,
#elif EVB_NUMLEDS >= 5
    0x10, 0x08, 0x04, 0x02, 0x01, 0x10, 0x08, 0x04, 0x02, 0x01, 0x00,
#endif

    //
    // Springing pattern
    //
#if EVB_NUMLEDS == 3
    0x15, 0x0A, 0x15, 0x0A, 0x15, 0x0A, 0x15, 0x0A,
    0x15, 0x0A, 0x15, 0x0A, 0x15, 0x0A, 0x15, 0x0A,
#else
    0x15, 0x0A, 0x15, 0x0A, 0x15, 0x0A, 0x15, 0x0A, 0x15, 0x00
#endif
};

//*****************************************************************************
//
// Set or clear an LED.
//
// The LEDs on the Apollo510 EVB are common anode (anodes tied high).
// The emitter on the controlling transistor is connected to the GPIO.
// Therefore, the LEDs light when the GPIO is driven low (cleared).
//
//*****************************************************************************
static void
LED_state(uint32_t ui32LED, bool bOn)
{
    uint32_t *pui32WTC, *pui32WTS;
    uint32_t ui32Mask = 1 << (ui32LED % 32);

    if ( ui32LED > AM_HAL_PIN_TOTAL_GPIOS)
    {
        while(1);
    }

    if ( bOn )
    {
        pui32WTC = (uint32_t*)&GPIO->WTC0 + (ui32LED / 32);
        *pui32WTC = ui32Mask;
    }
    else
    {
        pui32WTS = (uint32_t*)&GPIO->WTS0 + (ui32LED / 32);
        *pui32WTS = ui32Mask;
    }

} // LED_state()

//*****************************************************************************
//
// Set a PADREG FNCSEL field.
//
//*****************************************************************************
static void
gpio_pincfg(uint32_t ui32GPIOnum)
{
    uint32_t volatile *pui32Reg;

    pui32Reg  = &GPIO->PINCFG0 + ui32GPIOnum;

    //
    // Unlock writes to the GPIO and PAD configuration registers.
    //
    GPIO->PADKEY = GPIO_PADKEY_PADKEY_Key;  // 0x73

    //
    // Set the pin configuration
    //
    *pui32Reg = _VAL2FLD(GPIO_PINCFG0_FNCSEL0,  GPIO_PINCFG0_FNCSEL0_GPIO)      |   // GPIO
                _VAL2FLD(GPIO_PINCFG0_INPEN0,   0)                              |   // Input disable
                _VAL2FLD(GPIO_PINCFG0_RDZERO0,  0)                              |   // No read data
                _VAL2FLD(GPIO_PINCFG0_IRPTEN0,  GPIO_PINCFG0_IRPTEN0_DIS)       |   // No interrupts
                _VAL2FLD(GPIO_PINCFG0_OUTCFG0,  GPIO_PINCFG0_OUTCFG0_PUSHPULL)  |   // PushPull
                _VAL2FLD(GPIO_PINCFG0_DS0,      GPIO_PINCFG0_DS0_0P1X)          |   // Normal drive strength
                _VAL2FLD(GPIO_PINCFG0_PULLCFG0, GPIO_PINCFG0_PULLCFG0_DIS);         // No pullup

    //
    // Lock PAD configuration registers.
    //
    GPIO->PADKEY = 0;

} // gpio_pincfg()

//*****************************************************************************
//
// Configure for SWO.
//
//*****************************************************************************
static void
swo_pincfg(uint32_t ui32GPIOnum)
{
    uint32_t volatile *pui32Reg;

    pui32Reg  = &GPIO->PINCFG0 + ui32GPIOnum;

    //
    // Unlock writes to the GPIO and PAD configuration registers.
    //
    GPIO->PADKEY = 0x73;

    //
    // Set the pin configuration
    //
    *pui32Reg = _VAL2FLD(GPIO_PINCFG0_FNCSEL0,  GPIO_PINCFG28_FNCSEL28_SWO)     |   // SWO
                _VAL2FLD(GPIO_PINCFG0_INPEN0,   0)                              |   // Input disable
                _VAL2FLD(GPIO_PINCFG0_RDZERO0,  0)                              |   // No read data
                _VAL2FLD(GPIO_PINCFG0_IRPTEN0,  GPIO_PINCFG0_IRPTEN0_DIS)       |   // No interrupts
                _VAL2FLD(GPIO_PINCFG0_OUTCFG0,  GPIO_PINCFG0_OUTCFG0_PUSHPULL)  |   // PushPull
                _VAL2FLD(GPIO_PINCFG0_DS0,      GPIO_PINCFG0_DS0_0P1X)          |   // Normal drive strength
                _VAL2FLD(GPIO_PINCFG0_PULLCFG0, GPIO_PINCFG0_PULLCFG0_DIS);         // No pullup

    //
    // Lock PAD configuration registers.
    //
    GPIO->PADKEY = 0;

} // gpio_pincfg()

//*****************************************************************************
//
// Configure a GPIO for use with an LED.
//
//*****************************************************************************
void
LED_gpio_cfg(uint32_t ui32GPIOnum)
{
    if ( ui32GPIOnum > AM_HAL_PIN_TOTAL_GPIOS )
    {
        //
        // Error
        //
        while(1);
    }

    //
    // Configure the given GPIO
    //
    gpio_pincfg(ui32GPIOnum);

} // LED_gpio_cfg()

//*****************************************************************************
//
// Initialize GPIO PADS to drive the LEDs and enable SWO
//
//*****************************************************************************
void
GPIO_init(void)
{
    //
    // Configure pads for LEDs as GPIO functions.
    //
    //
    LED_gpio_cfg(EVB_LED0);
    LED_gpio_cfg(EVB_LED1);
    LED_gpio_cfg(EVB_LED2);

    //
    // While we're at it, also configure for SWO.
    // For the Apollo510 EVB, this is pin 28.
    //
    swo_pincfg(28);

    //
    // Initialize the LEDs to all on.
    //
    LED_state(EVB_LED0, true);
    LED_state(EVB_LED1, true);
    LED_state(EVB_LED2, true);

} // GPIO_init()

//*****************************************************************************
//
// CTIMER_init
//
//*****************************************************************************
#define TIMER_NUM   0

void
CTIMER_init(void)
{
    //
    // Disable the timer
    //
    TIMER->CTRL0_b.TMR0EN   = TIMER_CTRL0_TMR0EN_DIS;

    //
    // Configure the timer
    // CTRL, MODE, CMP0, CMP1
    //
    TIMER->CTRL0_b.TMR0CLR  = TIMER_CTRL0_TMR0CLR_CLEAR;
    TIMER->CTRL0_b.TMR0POL0 = TIMER_CTRL0_TMR0POL0_NORMAL;
    TIMER->CTRL0_b.TMR0POL1 = TIMER_CTRL0_TMR0POL1_NORMAL;
    TIMER->CTRL0_b.TMR0FN   = TIMER_CTRL0_TMR0FN_UPCOUNT;
    TIMER->CTRL0_b.TMR0CLK  = TIMER_CTRL0_TMR0CLK_HFRC_DIV16;

    TIMER->MODE0_b.TMR0TRIGSEL = TIMER_MODE0_TMR0TRIGSEL_TMR01;

    TIMER->TMR0CMP0         = 0xFFFFFFFF;
    TIMER->TMR0CMP1         = 6000000;

    //
    // Clear the timer
    //
    TIMER->CTRL0_b.TMR0CLR = TIMER_CTRL0_TMR0CLR_CLEAR;
    TIMER->CTRL0_b.TMR0CLR = TIMER_CTRL0_TMR0CLR_DEFAULT;

    //
    // Interrupt clear
    //
    TIMER->INTCLR = 0x2 << TIMER_NUM;   // Clear CMP1

    //
    // Interrupt enable
    //
    TIMER->INTEN  |= 2 << TIMER_NUM;    // Enable CMP1

    //
    // Enable CTIMER interrupts in the NVIC.
    //
    NVIC_EnableIRQ(TIMER0_IRQn);
    __enable_irq();

    //
    // Start the timer
    //
    TIMER->CTRL0_b.TMR0EN  = TIMER_CTRL0_TMR0EN_EN;

} // CTIMER_init()

//*****************************************************************************
//
// setSleepMode
//
//*****************************************************************************
void
setSleepMode (int bSetDeepSleep)
{
    if ( bSetDeepSleep )
    {
        SCB->SCR |= SCB_SCR_SLEEPDEEP_Msk;
    }
    else
    {
        SCB->SCR &= ~SCB_SCR_SLEEPDEEP_Msk;
    }
} // setSleepMode()

//*****************************************************************************
//
// Timer interrupt service routine: increment software counter at 1 Second
//                                  intervals and output to the LEDs
//                                  Entered once per second
//
//*****************************************************************************
void
am_timer00_isr(void)
{
    uint32_t ui32Value;

    //
    // Clear the timer.
    //
    TIMER->CTRL0_b.TMR0CLR = TIMER_CTRL0_TMR0CLR_CLEAR;
    TIMER->CTRL0_b.TMR0CLR = TIMER_CTRL0_TMR0CLR_DEFAULT;

    //
    // Clear timer interrupt.
    //
    TIMER->INTCLR = 0x2 << TIMER_NUM;   // Clear CMP1

    //
    // Look up next interesting pattern.
    //
    ui32Value = led_pattern[ui32SoftwareCounter];

    //
    // Increment software counter
    //
    ++ui32SoftwareCounter;
    ui32SoftwareCounter &= (sizeof(led_pattern) - 1);

    //
    // Copy software counter to LEDs.
    //
    LED_state( EVB_LED0, (bool)(ui32Value & 0x00000001) );
    LED_state( EVB_LED1, (bool)(ui32Value & 0x00000002) );
    LED_state( EVB_LED2, (bool)(ui32Value & 0x00000004) );

} // am_ctimer_isr()

//*****************************************************************************
//
// Main
//
//*****************************************************************************
int
main(void)
{
    //
    // Initialize GPIO PADs we will use.
    //
    GPIO_init();

    //
    // Configure type of sleep (0=normal sleep, 1=deep sleep).
    //
    setSleepMode(1);

    //
    // Initialize timer.
    //
    CTIMER_init();

    //
    // Wait for the timer interrupt.
    //
    while(1)
    {
        //
        // Sleep here and wait for the timer to wake.
        //
        __WFI();
    }
} // main()
