#include "native_gomore_clear_two.h"
#include <stdint.h>
#include <stddef.h>
extern void __aeabi_memclr(void *,size_t);
void r1_gomore_clear_two_native(volatile void *record)
{
    uintptr_t state=(uintptr_t)record;
    __aeabi_memclr((void *)(uintptr_t)state,20);
    __aeabi_memclr((void *)(uintptr_t)(state+20u),20);
}
