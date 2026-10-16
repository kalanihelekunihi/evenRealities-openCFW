#include <stdint.h>

/* Native table starts at 0x200717b0. The master dispatcher admits only
 * connection IDs 1..3 and indexes 0x30-byte rows. Placement is a linker gate. */
uint8_t audio_ble_discovery_connection_records_200717b0[3u * 0x30u];
extern uint8_t audio_ble_atts_connection_rows[3u * 0x30u]
    __attribute__((alias("audio_ble_discovery_connection_records_200717b0")));

/* dmConnCb starts at native 0x200712a4. Its first 0x90 bytes hold three CCB
 * rows; stock dmConnReset writes configuration through offset 0xc3. The
 * remaining extent and final RAM placement still require a linker audit. */
uint8_t audio_ble_dm_conn_rows_200712a4[0xc4u];
extern uint8_t audio_ble_connection_records[0xc4u]
    __attribute__((alias("audio_ble_dm_conn_rows_200712a4")));
extern uint8_t audio_dm_connection_records[0xc4u]
    __attribute__((alias("audio_ble_dm_conn_rows_200712a4")));

/* Native 0x20074344 is incremented before storing record timestamp +0xc4. */
uint32_t audio_ble_pair_timestamp_counter_20074344;
