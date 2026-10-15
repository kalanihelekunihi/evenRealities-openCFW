#include <stdint.h>

/* Native 0x47b40c: extract the record's one-byte feature flag and
 * return a pointer to its trailing feature data through the second output. */
void audio_ble_pair_record_flags_47b40c(uint32_t record, void *flag, uint32_t *features)
{
    *(uint8_t *)flag = *(const volatile uint8_t *)(uintptr_t)(record + 0x84u);
    *features = record + 0x85u;
}
