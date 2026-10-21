/* Cordio dmConnCcbAlloc at stock Apollo Main 0x4b5c78. Row initialization
 * and success/failure trace paths follow the pinned body and dm_conn.c. */
#include <stdint.h>

extern uint8_t audio_dm_connection_records[];
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern void audio_ble_copy_address6_4d293c(void *, const void *);
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
static const char alloc_tag[] = "ALLOC";
static const char module[] = "DM";
static const char hci_tag[] = "HCI";
static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\dm\\dm_conn.c";
static const char function[] = "dmConnCcbAlloc";
static const char success_message[] = "dmConnCcbAlloc %d";
static const char failure_message[] = "dmConnCcbAlloc failed";

static void trace(const char *tag, uint32_t line, const char *message,
                  uint8_t connection, uint8_t has_connection)
{
    uint8_t level;
    if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&
        audio_ble_hci_vendor_compare_44b610(tag, error_tag, 3u) == 0)
        level = 1u;
    else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&
             audio_ble_hci_vendor_compare_44b610(tag, warning_tag, 4u) == 0)
        level = 2u;
    else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&
             audio_ble_hci_vendor_compare_44b610(tag, info_tag, 4u) == 0)
        level = 3u;
    else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u)
        level = 4u;
    else {
        if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
            audio_ble_hci_vendor_compare_44b610(module, hci_tag, 3u) != 0) {
            if (has_connection != 0u)
                audio_ble_hci_wsf_trace(tag, message, connection);
            else
                audio_ble_hci_wsf_trace(tag, message);
        }
        return;
    }
    if ((audio_log_flags() & 2u) != 0u) {
        if (has_connection != 0u)
            audio_log_extended(level, module, source, function, line,
                               message, connection);
        else
            audio_log_extended(level, module, source, function, line,
                               message);
    }
}

void *audio_ble_dm_conn_ccb_alloc_4b5c78(const void *address)
{
    for (uint32_t i = 0u; i < 3u; ++i) {
        uint8_t *c = audio_dm_connection_records + i * 0x30u;
        if (c[0x16u] != 0u)
            continue;
        audio_uart_buffer_zero(c, 0x30u, 0u);
        audio_ble_copy_address6_4d293c(c, address);
        c[0x0cu] = 0xffu;
        c[0x0du] = 0xffu;
        c[0x10u] = (uint8_t)(i + 1u);
        c[0x11u] = 0u;
        c[0x16u] = 1u;
        c[0x2cu] = 0u;
        trace(alloc_tag, 0xbeu, success_message, c[0x10u], 1u);
        return c;
    }
    trace(error_tag, 0xc4u, failure_message, 0u, 0u);
    return 0;
}
