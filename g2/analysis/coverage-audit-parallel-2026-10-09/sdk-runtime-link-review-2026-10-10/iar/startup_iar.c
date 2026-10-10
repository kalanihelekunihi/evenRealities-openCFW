//*****************************************************************************
//
//! @file startup_iar.c
//!
//! @brief Definitions for interrupt handlers, the vector table, and the stack.
//
//*****************************************************************************

//*****************************************************************************
//
// Copyright (c) 2026, Ambiq Micro, Inc.
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
// This is part of revision release_sdk5p2p0-66487dd10 of the AmbiqSuite Development Package.
//
//*****************************************************************************

//#include <stdint.h>
#include "apollo510.h"

//*****************************************************************************
//
// Enable the IAR extensions for this source file.
//
//*****************************************************************************
#pragma language = extended

//*****************************************************************************
//
// Weak function links.
//
//*****************************************************************************
#pragma weak MemManage_Handler      = HardFault_Handler
#pragma weak BusFault_Handler       = HardFault_Handler
#pragma weak UsageFault_Handler     = HardFault_Handler
#pragma weak SecureFault_Handler    = HardFault_Handler
#pragma weak SVC_Handler            = am_default_isr
#pragma weak DebugMon_Handler       = am_default_isr
#pragma weak PendSV_Handler         = am_default_isr
#pragma weak SysTick_Handler        = am_default_isr

#pragma weak am_brownout_isr        = am_default_isr
#pragma weak am_watchdog_isr        = am_default_isr
#pragma weak am_rtc_isr             = am_default_isr
#pragma weak am_vcomp_isr           = am_default_isr
#pragma weak am_ioslave_ios_isr     = am_default_isr
#pragma weak am_ioslave_acc_isr     = am_default_isr
#pragma weak am_iomaster0_isr       = am_default_isr
#pragma weak am_iomaster1_isr       = am_default_isr
#pragma weak am_iomaster2_isr       = am_default_isr
#pragma weak am_iomaster3_isr       = am_default_isr
#pragma weak am_iomaster4_isr       = am_default_isr
#pragma weak am_iomaster5_isr       = am_default_isr
#pragma weak am_iomaster6_isr       = am_default_isr
#pragma weak am_iomaster7_isr       = am_default_isr
#pragma weak am_uart_isr            = am_default_isr
#pragma weak am_uart1_isr           = am_default_isr
#pragma weak am_uart2_isr           = am_default_isr
#pragma weak am_uart3_isr           = am_default_isr
#pragma weak am_adc_isr             = am_default_isr
#pragma weak am_mspi0_isr           = am_default_isr
#pragma weak am_mspi1_isr           = am_default_isr
#pragma weak am_mspi2_isr           = am_default_isr
#pragma weak am_clkgen_isr          = am_default_isr
#pragma weak am_cryptosec_isr       = am_default_isr
#pragma weak am_sdio0_isr           = am_default_isr
#pragma weak am_usb_isr             = am_default_isr
#pragma weak am_gpu_isr             = am_default_isr
#pragma weak am_disp_isr            = am_default_isr
#pragma weak am_dsi_isr             = am_default_isr
#pragma weak am_stimer_cmpr0_isr    = am_default_isr
#pragma weak am_stimer_cmpr1_isr    = am_default_isr
#pragma weak am_stimer_cmpr2_isr    = am_default_isr
#pragma weak am_stimer_cmpr3_isr    = am_default_isr
#pragma weak am_stimer_cmpr4_isr    = am_default_isr
#pragma weak am_stimer_cmpr5_isr    = am_default_isr
#pragma weak am_stimer_cmpr6_isr    = am_default_isr
#pragma weak am_stimer_cmpr7_isr    = am_default_isr
#pragma weak am_stimerof_isr        = am_default_isr
#pragma weak am_audadc0_isr         = am_default_isr
#pragma weak am_dspi2s0_isr         = am_default_isr
#pragma weak am_dspi2s1_isr         = am_default_isr
#pragma weak am_pdm0_isr            = am_default_isr
#pragma weak am_mspi3_isr           = am_default_isr
#pragma weak am_gpio0_001f_isr      = am_default_isr
#pragma weak am_gpio0_203f_isr      = am_default_isr
#pragma weak am_gpio0_405f_isr      = am_default_isr
#pragma weak am_gpio0_607f_isr      = am_default_isr
#pragma weak am_gpio0_809f_isr      = am_default_isr
#pragma weak am_gpio0_a0bf_isr      = am_default_isr
#pragma weak am_gpio0_c0df_isr      = am_default_isr
#pragma weak am_gpio0_e0ff_isr      = am_default_isr
#pragma weak am_timer00_isr         = am_default_isr
#pragma weak am_timer01_isr         = am_default_isr
#pragma weak am_timer02_isr         = am_default_isr
#pragma weak am_timer03_isr         = am_default_isr
#pragma weak am_timer04_isr         = am_default_isr
#pragma weak am_timer05_isr         = am_default_isr
#pragma weak am_timer06_isr         = am_default_isr
#pragma weak am_timer07_isr         = am_default_isr
#pragma weak am_timer08_isr         = am_default_isr
#pragma weak am_timer09_isr         = am_default_isr
#pragma weak am_timer10_isr         = am_default_isr
#pragma weak am_timer11_isr         = am_default_isr
#pragma weak am_timer12_isr         = am_default_isr
#pragma weak am_timer13_isr         = am_default_isr
#pragma weak am_timer14_isr         = am_default_isr
#pragma weak am_timer15_isr         = am_default_isr
#pragma weak am_sdio1_isr           = am_default_isr
#pragma weak am_software0_isr       = am_default_isr
#pragma weak am_software1_isr       = am_default_isr
#pragma weak am_software2_isr       = am_default_isr
#pragma weak am_software3_isr       = am_default_isr
#pragma weak am_gpio1_001f_isr      = am_default_isr
#pragma weak am_gpio1_203f_isr      = am_default_isr
#pragma weak am_gpio1_405f_isr      = am_default_isr
#pragma weak am_gpio1_607f_isr      = am_default_isr
#pragma weak am_gpio1_809f_isr      = am_default_isr
#pragma weak am_gpio1_a0bf_isr      = am_default_isr
#pragma weak am_gpio1_c0df_isr      = am_default_isr
#pragma weak am_ioslave_fd0_isr     = am_default_isr
#pragma weak am_ioslave_fd0_acc_isr = am_default_isr
#pragma weak am_ioslave_fd1_isr     = am_default_isr
#pragma weak am_ioslave_fd1_acc_isr = am_default_isr
#pragma weak FloatingPoint_Handler  = am_default_isr
#pragma weak am_otp_isr             = am_default_isr


//*****************************************************************************
//
// Forward declaration of the default fault handlers.
//
//*****************************************************************************
extern __stackless void Reset_Handler(void);
extern __weak void NMI_Handler(void);
extern __weak void HardFault_Handler(void);
extern        void MemManage_Handler(void);
extern        void BusFault_Handler(void);
extern        void UsageFault_Handler(void);
extern        void SecureFault_Handler(void);
extern        void SVC_Handler(void);
extern        void DebugMon_Handler(void);
extern        void PendSV_Handler(void);
extern        void SysTick_Handler(void);
extern void am_brownout_isr(void);          // 0
extern void am_watchdog_isr(void);          // 1
extern void am_rtc_isr(void);               // 2
extern void am_vcomp_isr(void);             // 3
extern void am_ioslave_ios_isr(void);       // 4
extern void am_ioslave_acc_isr(void);       // 5
extern void am_iomaster0_isr(void);         // 6
extern void am_iomaster1_isr(void);         // 7
extern void am_iomaster2_isr(void);         // 8
extern void am_iomaster3_isr(void);         // 9
extern void am_iomaster4_isr(void);         // 10
extern void am_iomaster5_isr(void);         // 11
extern void am_iomaster6_isr(void);         // 12
extern void am_iomaster7_isr(void);         // 13
extern void am_uart_isr(void);              // 15
extern void am_uart1_isr(void);             // 16
extern void am_uart2_isr(void);             // 17
extern void am_uart3_isr(void);             // 18
extern void am_adc_isr(void);               // 19
extern void am_mspi0_isr(void);             // 20
extern void am_mspi1_isr(void);             // 21
extern void am_mspi2_isr(void);             // 22
extern void am_clkgen_isr(void);            // 23
extern void am_cryptosec_isr(void);         // 24
extern void am_sdio0_isr(void);             // 26
extern void am_usb_isr(void);               // 27
extern void am_gpu_isr(void);               // 28
extern void am_disp_isr(void);              // 29
extern void am_dsi_isr(void);               // 30
extern void am_stimer_cmpr0_isr(void);      // 32
extern void am_stimer_cmpr1_isr(void);      // 33
extern void am_stimer_cmpr2_isr(void);      // 34
extern void am_stimer_cmpr3_isr(void);      // 35
extern void am_stimer_cmpr4_isr(void);      // 36
extern void am_stimer_cmpr5_isr(void);      // 37
extern void am_stimer_cmpr6_isr(void);      // 38
extern void am_stimer_cmpr7_isr(void);      // 39
extern void am_stimerof_isr(void);          // 40
extern void am_audadc0_isr(void);           // 42
extern void am_dspi2s0_isr(void);           // 44
extern void am_dspi2s1_isr(void);           // 45
extern void am_pdm0_isr(void);              // 48
extern void am_mspi3_isr(void);             // 54
extern void am_gpio0_001f_isr(void);        // 56
extern void am_gpio0_203f_isr(void);        // 57
extern void am_gpio0_405f_isr(void);        // 58
extern void am_gpio0_607f_isr(void);        // 59
extern void am_gpio0_809f_isr(void);        // 60
extern void am_gpio0_a0bf_isr(void);        // 61
extern void am_gpio0_c0df_isr(void);        // 62
extern void am_gpio0_e0ff_isr(void);        // 63
extern void am_timer00_isr(void);           // 67
extern void am_timer01_isr(void);           // 68
extern void am_timer02_isr(void);           // 69
extern void am_timer03_isr(void);           // 70
extern void am_timer04_isr(void);           // 71
extern void am_timer05_isr(void);           // 72
extern void am_timer06_isr(void);           // 73
extern void am_timer07_isr(void);           // 74
extern void am_timer08_isr(void);           // 75
extern void am_timer09_isr(void);           // 76
extern void am_timer10_isr(void);           // 77
extern void am_timer11_isr(void);           // 78
extern void am_timer12_isr(void);           // 79
extern void am_timer13_isr(void);           // 80
extern void am_timer14_isr(void);           // 81
extern void am_timer15_isr(void);           // 82
extern void am_sdio1_isr(void);             // 84
extern void am_software0_isr(void);         // 92
extern void am_software1_isr(void);         // 93
extern void am_software2_isr(void);         // 94
extern void am_software3_isr(void);         // 95
extern void am_ioslave_fd0_isr(void);       // 96
extern void am_ioslave_fd0_acc_isr(void);   // 97
extern void am_ioslave_fd1_isr(void);       // 98
extern void am_ioslave_fd1_acc_isr(void);   // 99
extern void am_gpio1_001f_isr(void);        // 125
extern void am_gpio1_203f_isr(void);        // 126
extern void am_gpio1_405f_isr(void);        // 127
extern void am_gpio1_607f_isr(void);        // 128
extern void am_gpio1_809f_isr(void);        // 129
extern void am_gpio1_a0bf_isr(void);        // 130
extern void am_gpio1_c0df_isr(void);        // 131
extern void FloatingPoint_Handler(void);    // 133
extern void am_otp_isr(void);               // 134

extern void am_default_isr(void);

//*****************************************************************************
//
// The entry point for the application startup code.
//
//*****************************************************************************
extern void __iar_program_start(void);

//*****************************************************************************
//
// Reserve space for the system stack.
//
//*****************************************************************************
static uint32_t pui32Stack[1024] @ ".stack";

//*****************************************************************************
//
// A union that describes the entries of the vector table.  The union is needed
// since the first entry is the stack pointer and the remainder are function
// pointers.
//
//*****************************************************************************
typedef union
{
    void (*pfnHandler)(void);
    uint32_t ui32Ptr;
}
uVectorEntry;

//*****************************************************************************
//
// The vector table.
//
// Proper alignment of the vector table is dependent on the number of
// external (peripheral) interrupts, see the following table for proper
// vectorbaseaddress alignment.
//     0-16      32-word
//    17-48      64-word
//    49-112    128-word  (Apollo510)
//   113-240    256-word
//
// The Apollo510 vector table must be located on a 512 byte boundary.
//
// Note: Aliasing and weakly exporting am_mpufault_isr, am_busfault_isr, and
// am_usagefault_isr does not work if am_fault_isr is defined externally.
// Therefore, we'll explicitly use am_fault_isr in the table for those vectors.
//
//*****************************************************************************
__root const uVectorEntry __vector_table[] @ ".intvec" =
{
    { .ui32Ptr = (uint32_t)pui32Stack + sizeof(pui32Stack) },
                                            // The initial stack pointer
    Reset_Handler,                          // The reset handler
    NMI_Handler,                            // The NMI handler
    HardFault_Handler,                      // The hard fault handler
    MemManage_Handler,                      // The MemManage_Handler
    BusFault_Handler,                       // The BusFault_Handler
    UsageFault_Handler,                     // The UsageFault_Handler
    SecureFault_Handler,                    // The Secure Fault Handler
    0,                                      // Reserved
    0,                                      // Reserved
    0,                                      // Reserved
    SVC_Handler,                            // SVCall handler
    DebugMon_Handler,                       // Debug monitor handler
    0,                                      // Reserved
    PendSV_Handler,                         // The PendSV handler
    SysTick_Handler,                        // The SysTick handler

    //
    // Peripheral Interrupts
    //
    am_brownout_isr,                        //  0: Brownout (rstgen)
    am_watchdog_isr,                        //  1: Watchdog (WDT)
    am_rtc_isr,                             //  2: RTC
    am_vcomp_isr,                           //  3: Voltage Comparator
    am_ioslave_ios_isr,                     //  4: I/O Slave general
    am_ioslave_acc_isr,                     //  5: I/O Slave access
    am_iomaster0_isr,                       //  6: I/O Master 0
    am_iomaster1_isr,                       //  7: I/O Master 1
    am_iomaster2_isr,                       //  8: I/O Master 2
    am_iomaster3_isr,                       //  9: I/O Master 3
    am_iomaster4_isr,                       // 10: I/O Master 4
    am_iomaster5_isr,                       // 11: I/O Master 5
    am_iomaster6_isr,                       // 12: I/O Master 6 (I3C/I2C/SPI)
    am_iomaster7_isr,                       // 13: I/O Master 7 (I3C/I2C/SPI)
    am_default_isr,                         // 14: Reserved
    am_uart_isr,                            // 15: UART0
    am_uart1_isr,                           // 16: UART1
    am_uart2_isr,                           // 17: UART2
    am_uart3_isr,                           // 18: UART3
    am_adc_isr,                             // 19: ADC
    am_mspi0_isr,                           // 20: MSPI0
    am_mspi1_isr,                           // 21: MSPI1
    am_mspi2_isr,                           // 22: MSPI2
    am_clkgen_isr,                          // 23: ClkGen
    am_cryptosec_isr,                       // 24: Crypto Secure
    am_default_isr,                         // 25: Reserved
    am_sdio0_isr,                           // 26: SDIO0
    am_usb_isr,                             // 27: USB
    am_gpu_isr,                             // 28: GPU
    am_disp_isr,                            // 29: DISP
    am_dsi_isr,                             // 30: DSI
    am_default_isr,                         // 31: Reserved
    am_stimer_cmpr0_isr,                    // 32: System Timer Compare0
    am_stimer_cmpr1_isr,                    // 33: System Timer Compare1
    am_stimer_cmpr2_isr,                    // 34: System Timer Compare2
    am_stimer_cmpr3_isr,                    // 35: System Timer Compare3
    am_stimer_cmpr4_isr,                    // 36: System Timer Compare4
    am_stimer_cmpr5_isr,                    // 37: System Timer Compare5
    am_stimer_cmpr6_isr,                    // 38: System Timer Compare6
    am_stimer_cmpr7_isr,                    // 39: System Timer Compare7
    am_stimerof_isr,                        // 40: System Timer Cap Overflow
    am_default_isr,                         // 41: Reserved
    am_audadc0_isr,                         // 42: Audio ADC
    am_default_isr,                         // 43: Reserved
    am_dspi2s0_isr,                         // 44: I2S0
    am_dspi2s1_isr,                         // 45: I2S1
    am_default_isr,                         // 46: Reserved
    am_default_isr,                         // 47: Reserved
    am_pdm0_isr,                            // 48: PDM0
    am_default_isr,                         // 49: Reserved
    am_default_isr,                         // 50: Reserved
    am_default_isr,                         // 51: Reserved
    am_default_isr,                         // 52: Reserved
    am_default_isr,                         // 53: Reserved
    am_mspi3_isr,                           // 54: MSPI3
    am_default_isr,                         // 55: Reserved
    am_gpio0_001f_isr,                      // 56: GPIO N0 pins  0-31
    am_gpio0_203f_isr,                      // 57: GPIO N0 pins 32-63
    am_gpio0_405f_isr,                      // 58: GPIO N0 pins 64-95
    am_gpio0_607f_isr,                      // 59: GPIO N0 pins 96-127
    am_gpio0_809f_isr,                      // 60: GPIO N0 pins 128-159
    am_gpio0_a0bf_isr,                      // 61: GPIO N0 pins 160-191
    am_gpio0_c0df_isr,                      // 62: GPIO N0 pins 192-223
    am_gpio0_e0ff_isr,                      // 63: GPIO N0 pins 224-256
    am_default_isr,                         // 64: Reserved
    am_default_isr,                         // 65: Reserved
    am_default_isr,                         // 66: Reserved
    am_timer00_isr,                         // 67: timer0
    am_timer01_isr,                         // 68: timer1
    am_timer02_isr,                         // 69: timer2
    am_timer03_isr,                         // 70: timer3
    am_timer04_isr,                         // 71: timer4
    am_timer05_isr,                         // 72: timer5
    am_timer06_isr,                         // 73: timer6
    am_timer07_isr,                         // 74: timer7
    am_timer08_isr,                         // 75: timer8
    am_timer09_isr,                         // 76: timer9
    am_timer10_isr,                         // 77: timer10
    am_timer11_isr,                         // 78: timer11
    am_timer12_isr,                         // 79: timer12
    am_timer13_isr,                         // 80: timer13
    am_timer14_isr,                         // 81: timer14
    am_timer15_isr,                         // 82: timer15
    am_default_isr,                         // 83: Reserved
    am_sdio1_isr,                           // 84: SDIO1
    am_default_isr,                         // 85: Reserved
    am_default_isr,                         // 86: Reserved
    am_default_isr,                         // 87: Reserved
    am_default_isr,                         // 88: Reserved
    am_default_isr,                         // 89: Reserved
    am_default_isr,                         // 90: Reserved
    am_default_isr,                         // 91: Reserved
    am_software0_isr,                       // 92: SOFTWARE0
    am_software1_isr,                       // 93: SOFTWARE1
    am_software2_isr,                       // 94: SOFTWARE2
    am_software3_isr,                       // 95: SOFTWARE3
    am_ioslave_fd0_isr,                     // 96: IOSFD0
    am_ioslave_fd0_acc_isr,                 // 97: IOSFDACC0
    am_ioslave_fd1_isr,                     // 98: IOSFD1
    am_ioslave_fd1_acc_isr,                 // 99: IOSFDACC1
    am_default_isr,                         // 100: Reserved
    am_default_isr,                         // 101: Reserved
    am_default_isr,                         // 102: Reserved
    am_default_isr,                         // 103: Reserved
    am_default_isr,                         // 104: Reserved
    am_default_isr,                         // 105: Reserved
    am_default_isr,                         // 106: Reserved
    am_default_isr,                         // 107: Reserved
    am_default_isr,                         // 108: Reserved
    am_default_isr,                         // 109: Reserved
    am_default_isr,                         // 110: Reserved
    am_default_isr,                         // 111: Reserved
    am_default_isr,                         // 112: Reserved
    am_default_isr,                         // 113: Reserved
    am_default_isr,                         // 114: Reserved
    am_default_isr,                         // 115: Reserved
    am_default_isr,                         // 116: Reserved
    am_default_isr,                         // 117: Reserved
    am_default_isr,                         // 118: Reserved
    am_default_isr,                         // 119: Reserved
    am_default_isr,                         // 120: Reserved
    am_default_isr,                         // 121: Reserved
    am_default_isr,                         // 122: Reserved
    am_default_isr,                         // 123: Reserved
    am_default_isr,                         // 124: Reserved
    am_gpio1_001f_isr,                      // 125: GPIO N1 pins  0-31
    am_gpio1_203f_isr,                      // 126: GPIO N1 pins 32-63
    am_gpio1_405f_isr,                      // 127: GPIO N1 pins 64-95
    am_gpio1_607f_isr,                      // 128: GPIO N1 pins 96-127
    am_gpio1_809f_isr,                      // 129: GPIO N1 pins 128-159
    am_gpio1_a0bf_isr,                      // 130: GPIO N1 pins 160-191
    am_gpio1_c0df_isr,                      // 131: GPIO N1 pins 192-223
    am_default_isr,                         // 132: Reserved
    FloatingPoint_Handler,                  // 133: Floating Point Exception
    am_otp_isr                              // 134: OTP
};

//******************************************************************************
//
// Place code immediately following vector table.
//
//******************************************************************************
//******************************************************************************
//
// The Patch table.
//
// The patch table should pad the vector table size to a total of 128 entries
// such that the code begins at 0x200.
// In other words, the final peripheral IRQ is always IRQ 111 (0-based).
//
//******************************************************************************
__root const uint32_t __Patchable[] @ ".patch" =
{
                   0, 0, 0, 0, 0,           // 135-139
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,           // 140-149
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,           // 150-159
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,           // 160-169
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,           // 170-179
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,           // 180-189
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,           // 190-199
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,           // 200-209
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,           // 210-219
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,           // 220-229
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0            // 230-239
};

// define the start of the patch table - at what would be vector 135
const uint32_t  * const __pPatchable =  (uint32_t *) __Patchable;

//*****************************************************************************
//
// Note - The template for this function is originally found in IAR's module,
//        low_level_init.c. As supplied by IAR, it is an empty function.
//
// This module contains the function `__low_level_init', a function
// that is called before the `main' function of the program.  Normally
// low-level initializations - such as setting the prefered interrupt
// level or setting the watchdog - can be performed here.
//
// Note that this function is called before the data segments are
// initialized, this means that this function cannot rely on the
// values of global or static variables.
//
// When this function returns zero, the startup code will inhibit the
// initialization of the data segments. The result is faster startup,
// the drawback is that neither global nor static data will be
// initialized.
//
// Copyright 1999-2017 IAR Systems AB.
//
// $Revision: 112610 $
//
//
//
//
//*****************************************************************************
#define AM_REGVAL(x)               (*((volatile uint32_t *)(x)))
#define VTOR_ADDR                   0xE000ED08

__interwork int __low_level_init(void)
{

    AM_REGVAL(VTOR_ADDR) = (uint32_t)&__vector_table;

    /*==================================*/
    /* Choose if segment initialization */
    /* should be done or not.           */
    /* Return: 0 to omit seg_init       */
    /*         1 to run seg_init        */
    /*==================================*/
    return 1;
}

//*****************************************************************************
//
// This is the code that gets called when the processor first starts execution
// following a reset event.  Only the absolutely necessary set is performed,
// after which the application supplied entry() routine is called.
//
//*****************************************************************************
void
Reset_Handler(void)
{
    //
    // Set the stack limits
    // Note: Stack limits are not set by __iar_program_start().
    //
    __set_MSPLIM((uint32_t)&pui32Stack);
    __set_PSPLIM((uint32_t)&pui32Stack);

//
// Set the SSRAM non-cacheable for application explicitly requested SSRAM_NON_CACHEABLE
//
#ifdef SSRAM_NON_CACHEABLE
    __DSB();
    //
    // Set up non-cachable MPU region attributes.
    //
    ARM_MPU_SetMemAttr (
        7, // use the last MPU attribute slot
        ARM_MPU_ATTR (
        ARM_MPU_ATTR_MEMORY_ (0, 1, 0, 0),
        ARM_MPU_ATTR_MEMORY_ (0, 1, 0, 0)
        )
    );

    //
    // Set the whole SSRAM non-cacheable
    //
    static ARM_MPU_Region_t region;
    region.RBAR = ((0x20080000 & MPU_RBAR_BASE_Msk) |
                    (ARM_MPU_SH_NON << MPU_RBAR_SH_Pos) |
                    (ARM_MPU_AP_(0, 1) << MPU_RBAR_AP_Pos) |
                    (1 << MPU_RBAR_XN_Pos));
    region.RLAR = ((0x2037FFFF & MPU_RLAR_LIMIT_Msk) |
                    (7 << MPU_RLAR_AttrIndx_Pos) |
                    (1));
    ARM_MPU_Load (
        15, // use the last MPU region
        (ARM_MPU_Region_t const*)&region, 1);

    //
    // Enable MPU
    //
#pragma diag_suppress = Go004
    SCB_CleanInvalidateDCache();
#pragma diag_default = Go004
    ARM_MPU_Enable((1 << MPU_CTRL_HFNMIENA_Pos) |
                    (1 << MPU_CTRL_PRIVDEFENA_Pos));

#endif // SSRAM_NON_CACHEABLE

    //
    // Call the application's entry point.
    //
    __iar_program_start();

    //SystemInit();
}

//*****************************************************************************
//
// This is the code that gets called when the processor receives a NMI.  This
// simply enters an infinite loop, preserving the system state for examination
// by a debugger.
//
//*****************************************************************************
__weak void
NMI_Handler(void)
{
    //
    // Enter into an infinite loop.
    //
    while(1)
    {
    }
}

//*****************************************************************************
//
// This is the code that gets called when the processor receives a fault
// interrupt.  This simply enters an infinite loop, preserving the system state
// for examination by a debugger.
//
//*****************************************************************************
__weak void
HardFault_Handler(void)
{
    //
    // Enter into an infinite loop.
    //
    while(1)
    {
    }
}

//*****************************************************************************
//
// This is the code that gets called when the processor receives an unexpected
// interrupt.  This simply enters an infinite loop, preserving the system state
// for examination by a debugger.
//
//*****************************************************************************
void
am_default_isr(void)
{
    //
    // Enter into an infinite loop.
    //
    while(1)
    {
    }
}

