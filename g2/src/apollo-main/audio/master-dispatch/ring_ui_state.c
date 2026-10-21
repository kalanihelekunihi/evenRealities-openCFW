#include <stddef.h>
#include <stdint.h>

/* Native ring handler state 0x20074074, shared by init and send paths. */
struct audio_ble_ring_handler_state {
    uint8_t active;
    uint8_t handler;
    uint16_t reserved;
    uint16_t *service_handles;
    uint16_t initialized;
};
_Static_assert(sizeof(struct audio_ble_ring_handler_state) == 12, "ring state size");
_Static_assert(offsetof(struct audio_ble_ring_handler_state, service_handles) == 4,
               "ring handle pointer offset");
_Static_assert(offsetof(struct audio_ble_ring_handler_state, initialized) == 8,
               "ring initialized offset");
struct audio_ble_ring_handler_state audio_ble_ring_handler_state;

/* Native AppUi callbacks 0x20073f60..0x20073f6b; reset uses cell +8. */
uintptr_t audio_ble_ui_callback_cells[3];
