/* Cordio legacy advertising HCI event handler, native Thumb 0x4ba4b0. */
#include <stdint.h>

extern uint8_t audio_ble_dm_adv_control[];
extern uint8_t audio_ble_dm_handler_state[];
extern uint8_t audio_ble_dm_leg_adv_type_20074fb3;
extern void audio_ble_dm_adv_reset_4ba45c(void);
extern void audio_ble_dm_adv_msg_handler_4ba6ac(void *message);
extern void WsfTimerStartMs(void *timer, uint32_t milliseconds);
extern void WsfTimerStop(void *timer);
extern void dmDevPassEvtToDevPriv(uint8_t event, uint8_t parameter,
                                 uint8_t zero_a, uint8_t zero_b);
extern void audio_ble_dm_adv_gen_conn_complete_4b310a(uint8_t handle, uint8_t status);

static uint16_t audio_ble_dm_adv_duration(void)
{
    return (uint16_t)((uint16_t)audio_ble_dm_adv_control[0x20u] |
                      ((uint16_t)audio_ble_dm_adv_control[0x21u] << 8));
}

void audio_ble_dm_adv_hci_handler_4ba4b0(void *event)
{
    uint8_t *bytes = (uint8_t *)event;
    if (bytes[2u] != 0x35u) return;

    uint8_t callback_event = 0u;
    const uint8_t state = audio_ble_dm_adv_control[0x1du];
    const uint8_t status = bytes[3u];
    if (state == 2u || state == 3u) {
        if (status == 0u) {
            if (state == 3u) {
                const uint16_t duration = audio_ble_dm_adv_duration();
                if (duration != 0u) {
                    audio_ble_dm_adv_control[0x0au] = 7u;
                    WsfTimerStartMs(audio_ble_dm_adv_control, duration);
                }
                if (audio_ble_dm_leg_adv_type_20074fb3 != 4u) callback_event = 0x21u;
            }
            dmDevPassEvtToDevPriv(0x0cu, 0x21u, 0u, 0u);
            audio_ble_dm_adv_control[0x18u] = audio_ble_dm_leg_adv_type_20074fb3;
            audio_ble_dm_adv_control[0x1du] = 1u;
        } else {
            audio_ble_dm_adv_control[0x1du] = 0u;
        }
    } else if (state == 4u || state == 5u) {
        if (status == 0u) {
            if (state == 5u) {
                WsfTimerStop(audio_ble_dm_adv_control);
                callback_event = audio_ble_dm_leg_adv_type_20074fb3 == 4u ? 2u : 0x22u;
            }
            dmDevPassEvtToDevPriv(0x0du, 0x22u, 0u, 0u);
            audio_ble_dm_adv_control[0x18u] = 0xffu;
            audio_ble_dm_adv_control[0x1du] = 0u;
        } else {
            audio_ble_dm_adv_control[0x1du] = 1u;
        }
    }

    if (callback_event == 2u) {
        audio_ble_dm_adv_gen_conn_complete_4b310a(0u, 0x3cu);
    } else if (callback_event != 0u) {
        typedef void (*audio_dm_callback_t)(void *);
        bytes[2u] = callback_event;
        (*(audio_dm_callback_t *)(void *)(audio_ble_dm_handler_state + 8u))(event);
    }
}

typedef struct {
    void (*reset)(void);
    void (*hci)(void *);
    void (*message)(void *);
} audio_ble_dm_adv_interface_t;

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(audio_ble_dm_adv_interface_t) == 12u, "Thumb pointer ABI");
#endif
const audio_ble_dm_adv_interface_t audio_ble_dm_adv_table
    __attribute__((used, aligned(4))) = {
        audio_ble_dm_adv_reset_4ba45c,
        audio_ble_dm_adv_hci_handler_4ba4b0,
        audio_ble_dm_adv_msg_handler_4ba6ac,
    };
