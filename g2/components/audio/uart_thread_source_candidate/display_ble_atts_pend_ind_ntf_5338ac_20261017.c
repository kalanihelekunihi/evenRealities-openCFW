/* Cordio attsPendIndNtfHandle, stock 0x5338ac..0x53390e. */
#include <stdint.h>

uint8_t audio_ble_atts_pend_ind_ntf_5338ac(uint8_t *ccb,
                                             void *packet_arg)
{
    const uint8_t *const packet = (const uint8_t *)packet_arg;
    if (packet[8] == 0x1du)
        return (uint8_t)(*(const uint16_t *)(const void *)(ccb + 0x28u) != 0u);
    const uint16_t handle = *(const uint16_t *)(const void *)(packet + 2u);
    uint8_t pending_count = 0u;
    for (uint32_t index = 0u; index < 10u; ++index) {
        const uint16_t pending =
            *(const uint16_t *)(const void *)(ccb + 0x2au + 2u * index);
        if (pending != 0u) {
            if (pending == handle)
                return 1u;
            ++pending_count;
        }
    }
    return (uint8_t)(pending_count >= 10u);
}
