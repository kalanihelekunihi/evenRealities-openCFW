#include <stdint.h>

/* audio_ble_comm_dm_dispatch_a (the name _bleCommHandler 0x4b7d32 uses for
 * native 0x532924) is an alias in ble/ble-discovery/display_ble_discovery_process.c. */

/* AppDbHandleResolvedAddr 0x47ab6c accepts indices 0..9 into 200-byte rows.
 * Absolute placement at 0x20067a30 remains a linker/startup gate. */
uint8_t audio_ble_dm_conn_state_table_20067a30[10u * 200u];
