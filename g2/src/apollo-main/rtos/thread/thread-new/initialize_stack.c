/* Cortex-M initial task exception frame, stock 0x44215a. */
#include <stdint.h>
typedef void (*thread_entry)(void *);
void *g2_thread_initialize_stack(void *top,void *base,
                                  thread_entry entry,void *argument) {
    uint32_t *p=(uint32_t *)top;
    *--p=0x01000000u;                     /* xPSR */
    *--p=(uint32_t)(uintptr_t)entry;      /* PC */
    *--p=0x0044207du;                     /* task-return error entry */
    *--p=0x12121212u;
    *--p=0x03030303u;
    *--p=0x02020202u;
    *--p=0x01010101u;
    *--p=(uint32_t)(uintptr_t)argument;
    *--p=0x11111111u;
    *--p=0x10101010u;
    *--p=0x09090909u;
    *--p=0x08080808u;
    *--p=0x07070707u;
    *--p=0x06060606u;
    *--p=0x05050505u;
    *--p=0x04040404u;
    *--p=0xfffffffdu;                     /* exception return to PSP */
    *--p=(uint32_t)(uintptr_t)base;
    return p;
}
