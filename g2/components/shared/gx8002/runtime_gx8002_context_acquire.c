/* SPDX-License-Identifier: MIT */
/* LvpGetContext with the recovered firmware's three-record allocation. */
#include <stddef.h>
#include <lvp_context.h>
typedef struct {
    LVP_CONTEXT context;
    unsigned char snpu_buffer[8480] __attribute__((aligned(16)));
} open_cfw_context_buffer;
_Static_assert(sizeof(open_cfw_context_buffer) == 8512, "Context record ABI");
_Static_assert(offsetof(open_cfw_context_buffer, snpu_buffer) == 32, "SNPU offset");
int open_cfw_gx8002_context_acquire(unsigned int index,
                                  LVP_CONTEXT *volatile *context,
                                  volatile unsigned int *size)
{
    volatile open_cfw_context_buffer *record =
        &((volatile open_cfw_context_buffer *)0x20027be0)[index % 3];
    /* Keep the selected record in a register to avoid three address literals.
     * This compiler constraint emits no instructions. */
    __asm__ volatile ("" : "+r" (record));
    record->context.ctx_header = (void *)0x20027b60;
    record->context.snpu_buffer = (void *)record->snpu_buffer;
    *context = (LVP_CONTEXT *)&record->context;
    *size = sizeof(*record);
    return 0;
}
