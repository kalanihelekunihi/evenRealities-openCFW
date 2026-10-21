/* The queue's stock priority-disinherit name enters Apollo 0x45596e.
 * Export it at the pinned FreeRTOS source function, preserving all list and
 * priority side effects of that direct entry. */
#include "../../rtos/mutex-disinherit/disinherit.c"

__asm__(".global stock_priority_disinherit\n"
        ".set stock_priority_disinherit, xTaskPriorityDisinherit\n");
