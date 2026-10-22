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


