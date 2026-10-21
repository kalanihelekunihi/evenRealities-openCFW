#include <stdint.h>

/* Stock 0x44a9ae: one byte at the authenticated RAM address. Placement and
 * initialization of the state byte remain an independent image concern. */
extern volatile uint8_t audio_log_policy_byte;
uint32_t audio_log_policy(uint32_t ignored) {
    (void)ignored;
    return audio_log_policy_byte;
}
