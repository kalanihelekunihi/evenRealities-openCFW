/* Cordio dmAdvConnected/dmAdvConnectFailed at stock Main
 * 0x4ba9d4/0x4bab04. Product logging follows the selected DM_TRACE form. */
#include <stdint.h>

extern uint8_t audio_ble_dm_adv_control[];
extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_ble_hci_vendor_compare_44b610(
    const void *, const void *, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *,
                               const char *, uint32_t, const char *, ...);
extern void audio_ble_hci_wsf_trace(const char *, const char *, ...);
extern void WsfTimerStop(void *);
extern void audio_ble_dm_dev_pass_priv_4b2ea6(uint8_t, uint8_t,
                                                uint32_t, uint32_t);

static const char error_tag[] = "ERR";
static const char warning_tag[] = "WARN";
static const char info_tag[] = "INFO";
static const char module[] = "DM";
static const char hci_tag[] = "HCI";
static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\dm\\dm_adv_leg.c";
static const char connected_function[] = "dmAdvConnected";
static const char failed_function[] = "dmAdvConnectFailed";
static const char connected_message[] = "dmAdvConnected: state: %d";
static const char failed_message[] = "dmAdvConnectFailed: state: %d";

static void trace_state(const char *function, uint32_t line,
                        const char *message, uint8_t state)
{
    uint8_t level;
    if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&
        audio_ble_hci_vendor_compare_44b610(info_tag, error_tag, 3u) == 0)
        level = 1u;
    else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&
             audio_ble_hci_vendor_compare_44b610(info_tag, warning_tag, 4u) == 0)
        level = 2u;
    else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&
             audio_ble_hci_vendor_compare_44b610(info_tag, info_tag, 4u) == 0)
        level = 3u;
    else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u)
        level = 4u;
    else {
        if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
            audio_ble_hci_vendor_compare_44b610(module, hci_tag, 3u) != 0)
            audio_ble_hci_wsf_trace(info_tag, message, state);
        return;
    }
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(level, module, source, function, line,
                           message, state);
}

static void finish_directed_connection(void)
{
    WsfTimerStop(audio_ble_dm_adv_control);
    audio_ble_dm_dev_pass_priv_4b2ea6(13u, 34u, 0u, 0u);
    audio_ble_dm_adv_control[0x18u] = 0xffu;
    audio_ble_dm_adv_control[0x1du] = 0u;
}

void audio_ble_dm_adv_connected_4ba9d4(void)
{
    trace_state(connected_function, 0x1efu, connected_message,
                audio_ble_dm_adv_control[0x1du]);
    finish_directed_connection();
}

void audio_ble_dm_adv_connect_failed_4bab04(void)
{
    trace_state(failed_function, 0x203u, failed_message,
                audio_ble_dm_adv_control[0x1du]);
    finish_directed_connection();
}
