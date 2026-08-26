#ifndef OPEN_CFW_RUNTIME_CMBACKTRACE_FAULT_ENTRY_H
#define OPEN_CFW_RUNTIME_CMBACKTRACE_FAULT_ENTRY_H

/*
 * Cortex-M exception entry for the source-owned CmBacktrace fault path.
 *
 * This symbol is deliberately not named HardFault_Handler.  Production may
 * bind it into the vector table only after a real G2 fault-injection run has
 * established that the recovered stack, logger, and FreeRTOS seams are safe.
 */
void open_cfw_cmbacktrace_hardfault_entry(void);

#endif
