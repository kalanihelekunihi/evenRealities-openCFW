/* R1-owned configuration callbacks, not reconstructed FreeRTOS internals.
 * Stock entries: 0x95BB8 and 0x95BD0. Each returns a 112-byte control reservation followed
 * by a 256-word stack. Layout evidence: FREERTOS-STATIC-MEMORY-CORRELATION.md.
 * Sections expose placement to the future stock linker layout; object
 * compilation does not establish their final RAM addresses. */
#include "FreeRTOS.h"
#include "task.h"
#include "timers.h"

/* The callback literals prove a 112-byte reservation, not sizeof the stock
 * provider type. This candidate uses 92 bytes; exact kernel config is open. */
_Static_assert(sizeof(StaticTask_t) <= 112, "candidate TCB must fit stock reservation");
union r1_task_control_reservation {
    StaticTask_t control;
    uint8_t reserved[112];
};
_Static_assert(sizeof(StackType_t) == 4, "stock stack words are four bytes");
_Static_assert(configMINIMAL_STACK_SIZE == 256, "stock idle stack is 256 words");
_Static_assert(configTIMER_TASK_STACK_DEPTH == 256, "stock timer stack is 256 words");

struct r1_static_task_memory {
    union r1_task_control_reservation reservation;
    StackType_t stack[256];
};
_Static_assert(sizeof(struct r1_static_task_memory) == 0x470, "stock task allocation extent");

static struct r1_static_task_memory idle_memory
    __attribute__((section(".r1.idle_task_memory"), aligned(4)));
static struct r1_static_task_memory timer_memory
    __attribute__((section(".r1.timer_task_memory"), aligned(4)));

void vApplicationGetIdleTaskMemory(StaticTask_t **control, StackType_t **stack,
                                 uint32_t *depth) {
    *control = &idle_memory.reservation.control;
    *stack = idle_memory.stack;
    *depth = 256;
}

void vApplicationGetTimerTaskMemory(StaticTask_t **control, StackType_t **stack,
                                  uint32_t *depth) {
    *control = &timer_memory.reservation.control;
    *stack = timer_memory.stack;
    *depth = 256;
}
