/* Native smpCfg_t at ROM 0x774d44, pointed to by bleCommHandlerInit.
 * Field values are decoded from the authenticated 24-byte typed object. */
#include <stdint.h>
typedef struct {
    uint32_t attempt_timeout_ms;
    uint8_t io_capability;
    uint8_t minimum_key_length;
    uint8_t maximum_key_length;
    uint8_t maximum_attempts;
    uint8_t authentication;
    uint8_t alignment[3];
    uint32_t maximum_attempt_timeout_ms;
    uint32_t attempt_decrement_timeout_ms;
    uint16_t attempt_exponent;
    uint8_t trailing_alignment[2];
} audio_smp_config_t;
_Static_assert(sizeof(audio_smp_config_t)==24u,"Cordio smpCfg_t ABI");
const audio_smp_config_t audio_ble_comm_registration_table = {
    .attempt_timeout_ms=3000u,
    .io_capability=3u,
    .minimum_key_length=7u,
    .maximum_key_length=16u,
    .maximum_attempts=3u,
    .authentication=1u,
    .maximum_attempt_timeout_ms=64000u,
    .attempt_decrement_timeout_ms=64000u,
    .attempt_exponent=2u,
};
