#ifndef R1_NATIVE_GOMORE_HISTORY_H
#define R1_NATIVE_GOMORE_HISTORY_H
#include <stdint.h>
/* Native 0x94938: pointer-width result is the raw record+40 address. */
uintptr_t r1_gomore_modulo5_native(volatile void *record,uint32_t secondary,uint32_t primary);
#endif
