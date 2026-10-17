#include <stdint.h>

extern uint32_t audio_platform_callbacks_initialize(void);

uint32_t stock_register_callbacks(void)
{
    return audio_platform_callbacks_initialize();
}
