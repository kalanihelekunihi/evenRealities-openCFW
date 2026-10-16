/* Ten 256-byte persistent records mapped at Apollo MRAM 0x007ff000.
 * This is a NOLOAD reservation, never an initializer for user bond data. */
#include <stdint.h>

enum { AUDIO_BLE_MRAM_RECORD_BYTES = 10u * 256u };

uint8_t audio_ble_mram_records_7ff000[AUDIO_BLE_MRAM_RECORD_BYTES]
    __attribute__((section(".bss.opencfw.mram.records"), aligned(16), used));
extern uint8_t audio_ble_privacy_nvm_records[AUDIO_BLE_MRAM_RECORD_BYTES]
    __attribute__((alias("audio_ble_mram_records_7ff000")));

_Static_assert(AUDIO_BLE_MRAM_RECORD_BYTES == 2560u, "persistent record extent");
