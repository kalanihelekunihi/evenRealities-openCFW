#include <stdint.h>

/* Native 0x31aeb4..0x31af36: build an LL test/vendor event message. The
 * payload length is 0 (mode 0), at least 4 (mode 2, range below 5 gives 4)
 * or a random value modulo range raised to 4 (mode 1). The header {handle,
 * 2, length, 0, length, 0} is encoded by native 0x31b9ac; a non-empty payload
 * starts with the 32-bit value (little endian) followed by bytes 4, 5, ...
 * Returns the message, or 0 without one. */
extern uintptr_t opencfw_em9305_child_32d598(void);
extern uint32_t opencfw_em9305_scan_random_30c478(void);
extern uint32_t opencfw_em9305_dispatch_child_31b9ac(uintptr_t out,uintptr_t in);

struct test_event_header {
    uint16_t handle;
    uint16_t type;
    uint16_t length;
    uint8_t reserved[6];
    uint16_t zero;
    uint16_t length_again;
    uint8_t status;
} __attribute__((aligned(4)));

uintptr_t opencfw_em9305_child_31aeb4(uint32_t handle, uint32_t mode, uint32_t range, uint32_t value)
{
    struct test_event_header header;
    uintptr_t message = opencfw_em9305_child_32d598();
    if (message == 0u) return 0u;
    uint32_t length = 0u;
    if (mode == 2u) {
        length = range < 5u ? 4u : range;
    } else if (mode == 1u) {
        int32_t random = (int32_t)(opencfw_em9305_scan_random_30c478() % range);
        length = (uint32_t)(random > 4 ? random : 4);
    }
    header.status = 0u;
    header.length_again = (uint16_t)length;
    header.zero = 0u;
    header.length = (uint16_t)length;
    header.type = 2u;
    header.handle = (uint16_t)handle;
    uint32_t offset = opencfw_em9305_dispatch_child_31b9ac(message, (uintptr_t)&header);
    if (length == 0u) return message;
    volatile uint8_t *payload = (volatile uint8_t *)(message + offset);
    payload[0] = (uint8_t)value;
    payload[3] = (uint8_t)(value >> 24);
    payload[2] = (uint8_t)(value >> 16);
    payload[1] = (uint8_t)(value >> 8);
    for (uint32_t index = 4u; index < length; ++index)
        payload[index] = (uint8_t)index;
    return message;
}
