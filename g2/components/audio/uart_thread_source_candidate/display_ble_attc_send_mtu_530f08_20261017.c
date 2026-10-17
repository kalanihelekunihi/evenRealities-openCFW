/* Cordio attcSendMtuReq; stock Main 0x530f08 including warning trace. */
#include <stdint.h>
extern void audio_ble_attc_free_pkt_531ac0(uint8_t *);
extern void audio_ble_attc_send_simple_530e30(uint8_t *);
extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *, const void *, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_ble_hci_wsf_trace(const char *, const char *, ...);
static const char error_tag[] = "ERR";
static const char warning_tag[] = "WARN";
static const char info_tag[] = "INFO";
static const char module[] = "ATT";
static const char hci_tag[] = "HCI";
static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\att\\attc_main.c";
static const char function[] = "attcSendMtuReq";
static const char message[] = "MTU req discarded";
void audio_ble_attc_send_mtu_530f08(uint8_t *ccb)
{
    uint8_t *main_ccb = *(uint8_t **)ccb;
    uint8_t *control = main_ccb + (uint32_t)ccb[0x0eu] * 4u + 2u;
    if ((*control & 1u) == 0u) {
        *control |= 1u;
        audio_ble_attc_send_simple_530e30(ccb);
        return;
    }
    audio_ble_attc_free_pkt_531ac0(ccb + 4u);
    ccb[6u] = 0u;
    uint8_t level;
    if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&
        audio_ble_hci_vendor_compare_44b610(warning_tag, error_tag, 3u) == 0)
        level = 1u;
    else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&
             audio_ble_hci_vendor_compare_44b610(warning_tag, warning_tag, 4u) == 0)
        level = 2u;
    else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&
             audio_ble_hci_vendor_compare_44b610(warning_tag, info_tag, 4u) == 0)
        level = 3u;
    else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u)
        level = 4u;
    else {
        if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
            audio_ble_hci_vendor_compare_44b610(module, hci_tag, 3u) != 0)
            audio_ble_hci_wsf_trace(warning_tag, message);
        return;
    }
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(level, module, source, function, 0x13cu, message);
}
