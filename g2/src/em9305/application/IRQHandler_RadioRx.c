/* SPDX-License-Identifier: MIT
 * Stock 0x306384 IRQHandler_RadioRx (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: the shared interrupt frame (em_irq_frame.h)
 * around RF_HandleInterrupt_Rx (0x311ab4, now C in RF_HandleInterrupt_Rx.c).
 * Not byte-identical: the stock frame saves the last aux register in the delay slot of the call, this one stores it before the call.
 */
#include "em_irq_frame.h"

extern void opencfw_em9305_RF_HandleInterrupt_Rx(void);

EM_IRQ_HANDLER(opencfw_em9305_IRQHandler_RadioRx, opencfw_em9305_RF_HandleInterrupt_Rx);
