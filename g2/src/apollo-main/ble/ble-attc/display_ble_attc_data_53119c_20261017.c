/* Cordio attcDataCback at stock Main 0x53119c. */
#include <stdint.h>

extern uint8_t *audio_ble_attc_ccb_by_handle_531a7c(uint16_t, uint8_t);
extern void audio_ble_attc_proc_rsp_4b5448(uint8_t *, uint16_t, const uint8_t *);
extern void audio_ble_attc_proc_ind_4b557a(uint8_t *, uint16_t, const uint8_t *);
extern void audio_ble_attc_proc_multi_ntf_4b53e4(uint8_t *, uint16_t,
                                                   const uint8_t *);
extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_ble_hci_vendor_compare_44b610(
    const void *, const void *, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *,
                               const char *, uint32_t, const char *, ...);
extern void audio_ble_hci_wsf_trace(const char *, const char *, ...);

static const char error_tag[] = "ERR";
static const char warning_tag[] = "WARN";
static const char info_tag[] = "INFO";
static const char module[] = "ATT";
static const char hci_tag[] = "HCI";
static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\att\\attc_main.c";
static const char function[] = "attcDataCback";
static const char message[] = "attc unknown opcode 0x%02x";

static void trace_unknown(uint8_t opcode)
{
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
            audio_ble_hci_wsf_trace(warning_tag, message, opcode);
        return;
    }
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(level, module, source, function, 0x20cu,
                           message, opcode);
}

void audio_ble_attc_data_53119c(uint16_t handle, uint16_t length,
                                  const uint8_t *packet)
{
    uint8_t *ccb = audio_ble_attc_ccb_by_handle_531a7c(handle, 0u);
    if (ccb == 0 || length == 0u)
        return;
    const uint8_t opcode = packet[8u];
    if (opcode <= 0x19u)
        audio_ble_attc_proc_rsp_4b5448(ccb, length, packet);
    else if (opcode == 0x1bu || opcode == 0x1du)
        audio_ble_attc_proc_ind_4b557a(ccb, length, packet);
    else if (opcode == 0x23u)
        audio_ble_attc_proc_multi_ntf_4b53e4(ccb, length, packet);
    else
        trace_unknown(opcode);
}
