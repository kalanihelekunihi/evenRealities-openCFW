/* Cordio AttcIndConfirm at stock Main 0x4b5838. */
#include <stdint.h>

extern uint8_t *audio_ble_attc_ccb_by_handle_531a7c(uint16_t, uint8_t);
extern uint8_t *attMsgAlloc(uint16_t);
extern void L2cDataReq(uint16_t, uint16_t, uint16_t, uint8_t *);
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
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\att\\attc_proc.c";
static const char function[] = "AttcIndConfirm";
static const char message[] = "Invalid connId in attcProcIndConfirm: %d";

static void trace_zero_connection(uint8_t connection)
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
            audio_ble_hci_wsf_trace(warning_tag, message, connection);
        return;
    }
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(level, module, source, function, 0x31au,
                           message, connection);
}

void audio_ble_attc_ind_confirm_4b5838(uint8_t connection)
{
    if (connection == 0u) {
        trace_zero_connection(connection);
        return;
    }
    uint8_t *ccb = audio_ble_attc_ccb_by_handle_531a7c(
        (uint16_t)(connection - 1u), 0u);
    if (ccb == 0)
        return;
    uint32_t raw = (uint32_t)ccb[0] | ((uint32_t)ccb[1] << 8) |
                   ((uint32_t)ccb[2] << 16) | ((uint32_t)ccb[3] << 24);
    uint8_t *main_ccb = (uint8_t *)(uintptr_t)raw;
    if ((main_ccb[2] & 0x12u) != 0x10u)
        return;
    uint8_t *packet = attMsgAlloc(9u);
    if (packet == 0)
        return;
    main_ccb[2] &= (uint8_t)~0x10u;
    packet[8] = 0x1eu;
    uint16_t handle = (uint16_t)main_ccb[12] |
                      ((uint16_t)main_ccb[13] << 8);
    L2cDataReq(4u, handle, 1u, packet);
}
