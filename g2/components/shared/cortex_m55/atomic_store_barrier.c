/* SPDX-License-Identifier: MIT */
/* Stock 0x004488EC: store the word before the full-system barrier. */
#include <stdint.h>
#include "cmsis_gcc.h"

void FUN_004488ec(volatile uint32_t *object, uint32_t value)
{
    *object = value;
    __DMB();
}
