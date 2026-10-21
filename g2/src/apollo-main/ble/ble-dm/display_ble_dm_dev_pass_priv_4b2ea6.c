/* Cordio dmDevPassEvtToDevPriv 0x4b2ea6.
 * Matches upstream dm_dev.c: the WSF header status byte is not initialized
 * before dispatch and is not used by dmDevPrivMsgHandler action selection. */
#include <stdint.h>

extern uint8_t audio_ble_dm_config[]; /* RAM 0x20000694 */
extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_ble_hci_vendor_compare_44b610(
    const void *, const void *, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *,
                               const char *, uint32_t, const char *, ...);
extern void audio_ble_hci_wsf_trace(const char *, const char *, ...);

struct audio_ble_priv_event {
    uint16_t param;
    uint8_t event;
    uint8_t status;
    uint8_t adv_handle;
    uint8_t connectable;
};
_Static_assert(sizeof(struct audio_ble_priv_event) == 6u,
               "Cordio device privacy event layout");

static const char error_tag[] = "ERR";
static const char warning_tag[] = "WARN";
static const char info_tag[] = "INFO";
static const char module[] = "DM";
static const char hci_tag[] = "HCI";
static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\dm\\dm_dev.c";
static const char function[] = "dmDevPassEvtToDevPriv";
static const char message[] =
    "dmDevPassEvtToDevPriv: event: %d, param: %d, advHandle: %d";

void audio_ble_dm_dev_pass_priv_4b2ea6(uint8_t event, uint8_t param,
                                        uint32_t adv_handle,
                                        uint32_t connectable)
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
            audio_ble_hci_wsf_trace(info_tag, message, event, param,
                                    (uint8_t)adv_handle);
        goto dispatch;
    }
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(level, module, source, function, 0xd6u,
                           message, event, param, (uint8_t)adv_handle);
dispatch:;
    struct audio_ble_priv_event record;
    record.param = param;
    record.event = event;
    record.adv_handle = (uint8_t)adv_handle;
    record.connectable = (uint8_t)connectable;
    const uint8_t *slot = audio_ble_dm_config + 4u;
    uint32_t owner = (uint32_t)slot[0u] | ((uint32_t)slot[1u] << 8u) |
                     ((uint32_t)slot[2u] << 16u) |
                     ((uint32_t)slot[3u] << 24u);
    void (*callback)(void *) = *(void (**)(void *))(void *)(uintptr_t)(owner + 8u);
    callback(&record);
}
