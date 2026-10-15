#include <stdint.h>

/* Native hciCb at 0x20073870. The pinned Cordio ARM layout is 36 bytes. */
uint8_t audio_ble_hci_stack_state_20073870[0x24] __attribute__((aligned(4)));

/* Distinct native DM row state at 0x200738dc; observed writes end at +0x18. */
uint8_t audio_ble_dm_stack_rows_200738dc[0x19] __attribute__((aligned(4)));
