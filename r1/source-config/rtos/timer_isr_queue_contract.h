#ifndef R1_TIMER_ISR_QUEUE_CONTRACT_H
#define R1_TIMER_ISR_QUEUE_CONTRACT_H
#include "queue_operations_contract.h"
/* The baseline header was first included before assertion configuration.
 * The authenticated ISR queue route calls the SDK priority validator. */
void vPortValidateInterruptPriority(void);
#undef portASSERT_IF_INTERRUPT_PRIORITY_INVALID
#define portASSERT_IF_INTERRUPT_PRIORITY_INVALID() vPortValidateInterruptPriority()
#endif
