#include <stdint.h>

/* Native 0x317c40..0x317ca8: derive the session key into +84 (cipher of
 * +421 under +405), copy the 8-byte IV from +437 to +100, reset the packet
 * counters (+456..+471, +125), set +124 when the role byte +2 is 0, and
 * notify the optional key hook at 0x8028c0 with the key and the connection
 * index (912-byte entries from *0x805c70). Returns the hook result or 0. */
extern uint32_t opencfw_em9305_radio_cipher_30ff0c(uintptr_t key,uintptr_t output,uintptr_t input);
extern void *opencfw_em9305_memcpy(void *destination, const void *source, uint32_t bytes);

uint32_t opencfw_em9305_child_317c40(uintptr_t record)
{
    uintptr_t session_key = record + 84u;
    (void)opencfw_em9305_radio_cipher_30ff0c(record + 405u, session_key, record + 421u);
    (void)opencfw_em9305_memcpy((void *)(record + 100u), (const void *)(record + 437u), 8u);
    uint32_t role = *(volatile uint8_t *)(record + 2u);
    uintptr_t hook = *(volatile uint32_t *)(uintptr_t)0x8028c0u;
    *(volatile uint32_t *)(record + 456u) = 0u;
    *(volatile uint8_t *)(record + 125u) = 0u;
    *(volatile uint32_t *)(record + 460u) = 0u;
    *(volatile uint32_t *)(record + 464u) = 0u;
    *(volatile uint32_t *)(record + 468u) = 0u;
    *(volatile uint8_t *)(record + 124u) = role == 0u;
    if (hook == 0u) return 0u;
    uintptr_t base = *(volatile uint32_t *)(uintptr_t)0x805c70u;
    uint8_t index = (uint8_t)((int32_t)(record - base) / 912);
    return ((uint32_t (*)(uintptr_t, uint32_t))hook)(session_key, index);
}
