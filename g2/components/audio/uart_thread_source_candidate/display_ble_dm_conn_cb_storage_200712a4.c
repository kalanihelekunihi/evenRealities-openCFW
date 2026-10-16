/* Cordio dmConnCb block at native RAM 0x200712a4.
 * Three 0x30-byte CCB rows start this block. The callback array begins at
 * offset 0x90, and native dmConnReset writes through offset 0xc3. */
#include <stdint.h>

_Static_assert(3u * 0x30u == 0x90u, "CCB rows precede callbacks");

uint8_t audio_dm_connection_records[0xc4u]
    __attribute__((aligned(4), used));

extern uint8_t audio_ble_dm_connection_registry[0xc4u]
    __attribute__((alias("audio_dm_connection_records"), used));
