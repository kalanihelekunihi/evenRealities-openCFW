/* Stock Terminal ring pointer 0x597324 and item lookup 0x59737c. */
#include <stdint.h>

extern uint8_t audio_td_state[0xa1dc]; /* stock 0x2010fd20 */
extern uint32_t audio_td_ring_index_wrap(uint8_t *ring, uint16_t logical_index);

uint32_t audio_terminal_resource_597324(void) {
    return (uint32_t)(uintptr_t)(audio_td_state + 0x1054u); /* stock 0x20110d74 */
}

uint32_t audio_terminal_item_59737c(uint32_t logical_index) {
    uint8_t *ring = audio_td_state + 0x1054u;
    uint16_t count = *(const uint16_t *)(const void *)(ring + 0x8500u);
    uint16_t index = (uint16_t)logical_index;
    if (index >= count)
        return 0u;
    uint16_t physical = (uint16_t)audio_td_ring_index_wrap(ring, index);
    return (uint32_t)(uintptr_t)(ring + (uint32_t)physical * 0x214u);
}
