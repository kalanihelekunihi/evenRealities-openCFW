#include <stdint.h>

extern void audio_ble_discovery_process_532924(const uint8_t *);

/* Native _bleCommHandler 0x4b7d32 calls this same 0x532924 entry. */
void audio_ble_comm_dm_dispatch_a(void *message)
{
    audio_ble_discovery_process_532924((const uint8_t *)message);
}

/* AppDbHandleResolvedAddr 0x47ab6c accepts indices 0..9 into 200-byte rows.
 * Absolute placement at 0x20067a30 remains a linker/startup gate. */
uint8_t audio_ble_dm_conn_state_table_20067a30[10u * 200u];
