#include <stdint.h>

extern uint32_t xEventGroupClearBits(void *event_group, uint32_t bits);

/* Original 0x0800bf84..0x0800bf8c, timer-daemon callback. */
void vEventGroupClearBitsCallback(void *event_group, uint32_t bits)
{
    (void)xEventGroupClearBits(event_group, bits);
}
