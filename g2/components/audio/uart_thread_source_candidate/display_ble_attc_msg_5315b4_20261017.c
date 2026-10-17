/* Cordio attcMsgCback; stock Main 0x5315b4. Stock omits upstream timeout branch. */
#include <stdint.h>
extern uint8_t audio_ble_attc_state[];
extern uint8_t *audio_ble_attc_ccb_by_conn_id_531820(uint8_t, uint8_t);
extern void audio_ble_attc_free_pkt_531ac0(uint8_t *);
extern uint8_t audio_ble_attc_pend_write_cmd_530d74(const uint8_t *, uint16_t);
extern void audio_ble_attc_req_clear_531af2(uint8_t, uint8_t *, uint8_t);
extern void audio_ble_attc_setup_req_531160(uint8_t *, uint8_t *);
extern void WsfTimerStop(void *);
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
static const char function[] = "attcMsgCback";
static const char message[] = "attcMsgCback: msg: %#x slot: %#x";
static uint16_t read16(const uint8_t *p)
{
    return (uint16_t)p[0] | ((uint16_t)p[1] << 8);
}
static void trace_message(uint8_t event, uint8_t slot)
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
            audio_ble_hci_wsf_trace(info_tag, message, event, slot);
        return;
    }
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(level, module, source, function, 0x28bu,
                           message, event, slot);
}
void audio_ble_attc_msg_5315b4(uint8_t *msg)
{
    const uint8_t event = msg[2u];
    const uint8_t slot = msg[0x0au];
    trace_message(event, slot);
    if (event == 0x11u || event == 0x12u) {
        uint8_t *sign = *(uint8_t **)(audio_ble_attc_state + 0x1b0u);
        if (sign != 0u) {
            void (*callback)(void *, uint8_t *) = *(void (**)(void *, uint8_t *))sign;
            callback(0, msg);
        }
        return;
    }
    uint8_t *ccb = audio_ble_attc_ccb_by_conn_id_531820(msg[0u], slot);
    if (ccb == 0u) {
        if (event != 0u && event < 0x12u)
            audio_ble_attc_free_pkt_531ac0(msg);
        return;
    }
    uint8_t *on_deck = audio_ble_attc_state + 0x180u + (uint32_t)ccb[0x29u] * 12u;
    if (event <= 0x10u) {
        if ((ccb[0x28u] == 0u && on_deck[2u] != 0u) || ccb[6u] >= 2u ||
            (event == 0x0au && audio_ble_attc_pend_write_cmd_530d74(ccb, read16(msg + 8u)))) {
            audio_ble_attc_req_clear_531af2(ccb[0x29u], msg, 0x72u);
            return;
        }
        if (ccb[0x28u] == 0u && ccb[6u] == 1u) {
            for (uint32_t i = 0u; i < 12u; ++i) on_deck[i] = msg[i];
        } else {
            audio_ble_attc_setup_req_531160(ccb, msg);
        }
    } else if (event == 0x13u) {
        if (ccb[6u] != 0u && ccb[6u] != 1u) {
            WsfTimerStop(ccb + 0x18u);
            audio_ble_attc_req_clear_531af2(ccb[0x29u], ccb + 4u, 0x74u);
        } else if (ccb[0x28u] == 0u && on_deck[2u] != 0u) {
            audio_ble_attc_req_clear_531af2(ccb[0x29u], on_deck, 0x74u);
        }
    }
}
