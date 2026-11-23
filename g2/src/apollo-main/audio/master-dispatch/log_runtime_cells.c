/* Selected logger lock, sequence and policy cells at distinct native RAM. */
#include <stdint.h>

void *audio_log_lock_state __attribute__((section(".g2_ram_20074388")));
volatile uint8_t audio_log_sequence
    __attribute__((section(".g2_ram_20074f9f")));
volatile uint8_t audio_log_policy_byte
    __attribute__((section(".g2_ram_20004544"))) = 3u; /* stock .data init: 0x20004544 = 0x03 */
