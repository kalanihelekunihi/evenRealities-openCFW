/* SPDX-License-Identifier: MIT */
/* Stock 0x005939A0 reads PSP directly, without changing stack selection. */
#include <stdint.h>
#include "cmsis_gcc.h"

uint32_t FUN_005939a0(void)
{
    return __get_PSP();
}
