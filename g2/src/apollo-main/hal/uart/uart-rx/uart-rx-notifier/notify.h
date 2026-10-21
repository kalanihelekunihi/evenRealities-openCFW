#ifndef UART_RX_NOTIFIER_H
#define UART_RX_NOTIFIER_H
#include <stdint.h>
/* Only valid initialized task, notification index0, actions0..4 validated.
 * Waiting task must have event-item containerNULL and valid linked state item.
 * Suspended scheduler puts event item on pending-ready list, without switching. */
uint32_t uart_notify_isr(uint32_t task,uint32_t index,uint32_t value,uint32_t action,uint32_t *previous,uint32_t *woken);
#endif
