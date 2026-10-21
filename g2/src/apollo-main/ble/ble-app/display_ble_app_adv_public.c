/* Cordio app_slave_leg.c AppAdvStart/Stop/SetAdvType, checked against
 * Main native 0x4b2d22, 0x4b2d62 and 0x4b2d7c.  The application state and
 * configuration pointer are live product RAM, owned by its initializer. */
#include <stdint.h>

extern uint8_t audio_ble_subsystem_link_state_200719c8[];
extern const uint8_t *audio_ble_slave_registration_slot;
extern int appSlaveAdvMode(void);
extern void appSlaveAdvStart(uint8_t count, const uint8_t *handles,
                             const uint8_t *intervals, const uint8_t *durations,
                             const uint8_t *maximum_events, uint8_t restart,
                             uint8_t mode);
extern void appAdvStop(uint8_t count, const uint8_t *handles);
extern void appSetAdvType(uint8_t handle, uint8_t type,
                          uint16_t interval, uint16_t duration,
                          uint8_t maximum_events, uint8_t restart);

static uint16_t native_halfword(const uint8_t *p)
{
    return (uint16_t)p[0] | ((uint16_t)p[1] << 8u);
}

void AppAdvStart(uint8_t mode)
{
    if (appSlaveAdvMode()) {
        uint8_t handle = 0u;
        uint8_t maximum_events = 0u;
        audio_ble_subsystem_link_state_200719c8[0x57u] = 0u;
        appSlaveAdvStart(1u, &handle,
                         audio_ble_slave_registration_slot + 6u,
                         audio_ble_slave_registration_slot,
                         &maximum_events, 1u, mode);
    }
}

void AppAdvStop(void)
{
    if (appSlaveAdvMode()) {
        uint8_t handle = 0u;
        appAdvStop(1u, &handle);
    }
}

void AppSetAdvType(uint8_t type)
{
    if (appSlaveAdvMode()) {
        audio_ble_subsystem_link_state_200719c8[0x57u] = 0u;
        appSetAdvType(0u, type,
                      native_halfword(audio_ble_slave_registration_slot + 6u),
                      native_halfword(audio_ble_slave_registration_slot),
                      0u, 1u);
    }
}
