/* SPDX-License-Identifier: MIT */
/* Stock 0x004488F4: load the word, then order subsequent memory accesses.
 * Keep the volatile read before CMSIS's compiler + hardware barrier. */
#include <stdint.h>
#include "cmsis_gcc.h"

uint32_t FUN_004488f4(const volatile uint32_t *object)
{
    uint32_t value = *object;
    __DMB();
    return value;
}
