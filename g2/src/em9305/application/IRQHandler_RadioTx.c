/* SPDX-License-Identifier: MIT
 * Stock 0x306440 IRQHandler_RadioTx (g2-2.2.6.10 firmware_ble_em9305.bin). Wave 28: the shared interrupt frame (em_irq_frame.h)
 * around RF_HandleInterrupt_Tx (0x311c14, harness-checked against stock). Not byte-identical: the stock frame saves the last aux
 * register in the delay slot of the call, this one stores it before the call; the same values are saved and restored.
 */
#include "em_irq_frame.h"

extern void opencfw_em9305_RF_HandleInterrupt_Tx(void);

EM_IRQ_HANDLER(opencfw_em9305_IRQHandler_RadioTx, opencfw_em9305_RF_HandleInterrupt_Tx);
