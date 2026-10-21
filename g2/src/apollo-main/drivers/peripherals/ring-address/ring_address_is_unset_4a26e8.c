#include <stdint.h>

uint32_t audio_ring_address_is_unset_4a26e8(const uint8_t *address)
{
    if (address == 0) {
        return 1;
    }
    for (unsigned i = 0; i < 6; ++i) {
        if (address[i] != 0xffu) {
            return 0;
        }
    }
    return 1;
}
