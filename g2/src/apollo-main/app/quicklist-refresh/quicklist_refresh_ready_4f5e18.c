/* Apollo QuickList storage-to-UI mode dispatch 0x4f5e18..0x4f5e7b. */
#include <stdint.h>

extern uint32_t audio_quicklist_mode_one_4f5718(uint32_t);
extern uint32_t audio_quicklist_mode_two_4f5a1c(uint32_t);
extern uint32_t audio_quicklist_mode_two_detail_4f5838(uint32_t);
extern uint32_t audio_quicklist_mode_three_4f5c4c(uint32_t);

uint32_t audio_quicklist_refresh_ready_4f5e18(void) {
    const uint8_t mode = *(volatile uint8_t *)(uintptr_t)0x20102c3eu;
    const uint8_t detail = *(volatile uint8_t *)(uintptr_t)0x2012d579u;
    uint32_t result;
    if (mode == 1u)
        result = audio_quicklist_mode_one_4f5718(detail);
    else if (mode == 2u) {
        if (detail == 2u)
            result = audio_quicklist_mode_two_detail_4f5838(detail);
        else
            result = audio_quicklist_mode_two_4f5a1c(detail);
    } else if (mode == 3u)
        result = audio_quicklist_mode_three_4f5c4c(3u);
    else
        result = 3u;
    *(volatile uint8_t *)(uintptr_t)0x2012d578u = mode;
    return (uint8_t)result;
}
