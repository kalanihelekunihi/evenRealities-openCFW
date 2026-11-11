/* Native BLE connection-parameter and service-dispatch pointer cells. */
#include <stdint.h>

_Static_assert(sizeof(uintptr_t) == 4, "Apollo pointer cells must be words");

uint8_t *audio_ble_cached_conn_params
    __attribute__((section(".g2_ram_2007433c")));
uintptr_t audio_ble_service_dispatch_20074348
    __attribute__((section(".g2_ram_20074348")));
/* Stock 0x2007433c is a single cell (literal pool 0x477ab0/0x478700); alias so all users share it (Fix 31). */
extern uint8_t * audio_ble_msgtx_mode __attribute__((alias("audio_ble_cached_conn_params")));
