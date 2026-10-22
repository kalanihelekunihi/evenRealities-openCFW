/* Cordio dmConnSmExecute at stock Apollo Main 0x533ef4. The 80-byte state
 * table is pinned at 0x6ecc58; product traces around the Cordio transition
 * are preserved as separate INFO/ERR calls. */
#include <stdint.h>

extern uint8_t audio_ble_dm_master_state_a[]; /* stock RAM 0x20073fe4 */
extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_ble_hci_vendor_compare_44b610(
    const void *, const void *, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *,
                               const char *, uint32_t, const char *, ...);
extern void audio_ble_hci_wsf_trace(const char *, const char *, ...);

/* Stock 0x6ECC58 (dmConnStateTbl; upstream third-party/upstream/cordio/ble-host/sources/stack/dm/dm_conn_sm.c) */
__attribute__((used))
const uint8_t audio_ble_dm_conn_sm_state_table_6ecc58[5][8][2] = {
    {{1,16},{0,0},{2,32},{0,0},{3,34},{0,0},{0,0},{0,0}},
    {{1,0},{4,17},{1,0},{0,3},{3,2},{0,3},{1,0},{1,0}},
    {{2,0},{0,33},{2,0},{0,35},{3,34},{0,35},{2,0},{2,0}},
    {{3,0},{4,1},{3,0},{3,0},{3,0},{0,4},{3,5},{3,0}},
    {{4,0},{4,0},{4,0},{0,4},{4,1},{0,4},{4,0},{4,0}},
};
_Static_assert(sizeof(audio_ble_dm_conn_sm_state_table_6ecc58) == 80u,
               "Cordio connection state table extent");

static const char error_tag[] = "ERR";
static const char warning_tag[] = "WARN";
static const char info_tag[] = "INFO";
static const char module[] = "DM";
static const char hci_tag[] = "HCI";
static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\dm\\dm_conn_sm.c";
static const char function[] = "dmConnSmExecute";
static const char entry_message[] = "dmConnSmExecute pMsg->hdr.event=%d state=%d";
static const char transition_message[] =
    "dmConnSmExecute event=%d, action = %d, next state = %d";
static const char set_message[] = "dmConnSmExecute DM_CONN_ACT_SET_ID(action) =%d";
static const char id_message[] = "dmConnSmExecute DM_CONN_ACT_ID(action) =%d";
static const char invalid_message[] = "dmConnSmExecute: Invalid action set ID: %d";

static uint8_t level_for(const char *tag)
{
    if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&
        audio_ble_hci_vendor_compare_44b610(tag, error_tag, 3u) == 0)
        return 1u;
    if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&
        audio_ble_hci_vendor_compare_44b610(tag, warning_tag, 4u) == 0)
        return 2u;
    if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&
        audio_ble_hci_vendor_compare_44b610(tag, info_tag, 4u) == 0)
        return 3u;
    return audio_ble_hci_vendor_log_enabled_4c9c50() != 0u ? 4u : 0u;
}

static uint8_t wsf_allowed(void)
{
    return audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
           audio_ble_hci_vendor_compare_44b610(module, hci_tag, 3u) != 0;
}

static void trace1(const char *tag, uint32_t line, const char *message,
                   uint32_t a)
{
    uint8_t level = level_for(tag);
    if (level == 0u) {
        if (wsf_allowed()) audio_ble_hci_wsf_trace(tag, message, a);
    } else if ((audio_log_flags() & 2u) != 0u) {
        audio_log_extended(level, module, source, function, line, message, a);
    }
}

static void trace2(const char *tag, uint32_t line, const char *message,
                   uint32_t a, uint32_t b)
{
    uint8_t level = level_for(tag);
    if (level == 0u) {
        if (wsf_allowed()) audio_ble_hci_wsf_trace(tag, message, a, b);
    } else if ((audio_log_flags() & 2u) != 0u) {
        audio_log_extended(level, module, source, function, line, message, a, b);
    }
}

static void trace3(const char *tag, uint32_t line, const char *message,
                   uint32_t a, uint32_t b, uint32_t c)
{
    uint8_t level = level_for(tag);
    if (level == 0u) {
        if (wsf_allowed()) audio_ble_hci_wsf_trace(tag, message, a, b, c);
    } else if ((audio_log_flags() & 2u) != 0u) {
        audio_log_extended(level, module, source, function, line, message, a, b, c);
    }
}

void audio_ble_dm_conn_sm_execute_533ef4(void *ccb, void *message)
{
    uint8_t *c = (uint8_t *)ccb;
    uint8_t *m = (uint8_t *)message;
    uint8_t state = c[0x15u];
    trace2(info_tag, 0x8du, entry_message, m[2u], state);
    uint8_t event = m[2u] & 7u;
    uint8_t next = audio_ble_dm_conn_sm_state_table_6ecc58[state][event][0u];
    uint8_t action = audio_ble_dm_conn_sm_state_table_6ecc58[state][event][1u];
    c[0x15u] = next;
    trace3(info_tag, 0x98u, transition_message, event, action, next);
    uint8_t set_id = action >> 4u;
    uint8_t action_id = action & 0x0fu;
    trace1(info_tag, 0x9au, set_message, set_id);
    trace1(info_tag, 0x9bu, id_message, action_id);
    if (set_id < 3u) {
        const uint8_t *slot = audio_ble_dm_master_state_a + (uint32_t)set_id * 4u;
        uint32_t owner = (uint32_t)slot[0] | ((uint32_t)slot[1] << 8u) |
                         ((uint32_t)slot[2] << 16u) |
                         ((uint32_t)slot[3] << 24u);
        if (owner != 0u) {
            const uint8_t *entry = (const uint8_t *)(uintptr_t)(owner + (uint32_t)action_id * 4u);
            uint32_t function_address = (uint32_t)entry[0] |
                                        ((uint32_t)entry[1] << 8u) |
                                        ((uint32_t)entry[2] << 16u) |
                                        ((uint32_t)entry[3] << 24u);
            ((void (*)(void *, void *))(uintptr_t)function_address)(ccb, message);
        }
    } else {
        trace1(error_tag, 0xa0u, invalid_message, set_id);
    }
}
