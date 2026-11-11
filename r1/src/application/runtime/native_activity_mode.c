#include <stdint.h>
#include "native_sleep_wake.h"
__attribute__((section(".text.r1_activity_mode_byte_get")))
uint32_t r1_activity_mode_byte_get(void)
{
    return r1_activity_mode;
}
