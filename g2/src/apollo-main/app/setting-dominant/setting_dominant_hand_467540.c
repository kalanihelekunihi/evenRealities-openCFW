/* Stock setting_handle_dominant_hand, 0x467540..0x467c18. */
#include <stdint.h>

extern uint8_t *audio_setting_unit_record_get_466010(void);
extern int32_t g2_lfs_memcmp(const void *, const void *, uint32_t);
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t);
extern uint8_t audio_uart_device_role_get(void);
extern uint32_t audio_ring_connect_policy_on_hand_49f15a(uint32_t, uint32_t);
extern uint32_t audio_ring_address_is_unset_4a26e8(const void *);
extern void audio_ble_master_set_target_hand_4a2068(const void *, const void *, uint32_t);
extern void audio_uart_ring_unpair_publish_hand_4661a6(void);
extern void audio_uart_ring_unpair_commit_hand_466016(void);
extern void audio_ble_master_hand_changed_4a2948(uint32_t, uint32_t, uint32_t);
extern void audio_ble_status_reply(uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "setting";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\setting\\setting.c";
static const char function[] = "setting_handle_dominant_hand";
static const char null_message[] = "dominant_hand_data is NULL";
static const char null_short[] = "[setting]dominant_hand_data is NULL";
static const char received[] = "Received dominant_hand setting: dominant_hand=%u, ring_mac.size=%d";
static const char received_short[] = "[setting]Received dominant_hand setting: dominant_hand=%u, ring_mac.size=%d";
static const char old_high[] = "dominant_hand ring_mac changed, reconnect required old[5-3]=%02X:%02X:%02X:";
static const char old_high_short[] = "[setting]dominant_hand ring_mac changed, reconnect required old[5-3]=%02X:%02X:%02X:";
static const char old_low[] = "dominant_hand ring_mac changed, reconnect required old[2-0]=%02X:%02X:%02X";
static const char old_low_short[] = "[setting]dominant_hand ring_mac changed, reconnect required old[2-0]=%02X:%02X:%02X";
static const char new_high[] = "dominant_hand ring_mac changed, reconnect required new[5-3]=%02X:%02X:%02X:";
static const char new_high_short[] = "[setting]dominant_hand ring_mac changed, reconnect required new[5-3]=%02X:%02X:%02X:";
static const char new_low[] = "dominant_hand ring_mac changed, reconnect required new[2-0]=%02X:%02X:%02X";
static const char new_low_short[] = "[setting]dominant_hand ring_mac changed, reconnect required new[2-0]=%02X:%02X:%02X";
static const char policy[] = "dominant_hand policy: cur=%u new=%u role=%s";
static const char policy_short[] = "[setting]dominant_hand policy: cur=%u new=%u role=%s";
static const char recovered[] = "dominant_hand: ring_mac recovered from factory placeholder, delay connect %ums";
static const char recovered_short[] = "[setting]dominant_hand: ring_mac recovered from factory placeholder, delay connect %ums";
static const char updated[] = "Updated ring_mac=%02X:%02X:%02X:%02X:%02X:%02X";
static const char updated_short[] = "[setting]Updated ring_mac=%02X:%02X:%02X:%02X:%02X:%02X";
static const char absent[] = "ring_mac not provided by APP, keep local value";
static const char absent_short[] = "[setting]ring_mac not provided by APP, keep local value";
static const char bad_size[] = "Unexpected ring_mac size %d, ignore";
static const char bad_size_short[] = "[setting]Unexpected ring_mac size %d, ignore";
static const char unchanged[] = "setting_handle_dominant_hand: unchanged, refresh local kv%s";
static const char unchanged_short[] = "[setting]setting_handle_dominant_hand: unchanged, refresh local kv%s";
static const char rejected[] = "setting_handle_dominant_hand: rejected within switch window, keep cur=%u";
static const char rejected_short[] = "[setting]setting_handle_dominant_hand: rejected within switch window, keep cur=%u";

static void log0(uint8_t severity, uint32_t line, const char *format,
                 uint32_t short_level, const char *short_format)
{
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(severity, module, path, function, line, format);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(short_level, short_format, short_format);
}
static void log1(uint8_t severity, uint32_t line, const char *format,
                 uint32_t short_level, const char *short_format, uint32_t a)
{
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(severity, module, path, function, line, format, a);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(short_level, short_format, short_format, a);
}
static void log2(uint8_t severity, uint32_t line, const char *format,
                 uint32_t short_level, const char *short_format, uint32_t a, uint32_t b)
{
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(severity, module, path, function, line, format, a, b);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(short_level, short_format, short_format, a, b);
}
static void log3(uint8_t severity, uint32_t line, const char *format,
                 uint32_t short_level, const char *short_format,
                 uint32_t a, uint32_t b, uint32_t c)
{
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(severity, module, path, function, line, format, a, b, c);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(short_level, short_format, short_format, a, b, c);
}
static void log6(uint32_t line, const uint8_t *address)
{
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, line, updated,
                           address[5], address[4], address[3],
                           address[2], address[1], address[0]);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0d800000u, updated_short, updated_short,
                                    address[5], address[4], address[3],
                                    address[2], address[1], address[0]);
}
static void log_policy(uint8_t old_hand, uint8_t new_hand)
{
    if ((audio_log_flags() & 2u) != 0u) {
        const char *role = audio_uart_device_role_get() == 1u ? "RIGHT" : "LEFT";
        audio_log_extended(3u, module, path, function, 0x277u,
                           policy, old_hand, new_hand, role);
    }
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u) {
        const char *role = audio_uart_device_role_get() == 1u ? "RIGHT" : "LEFT";
        (void)compressed_log_output(0x0cc00000u, policy_short, policy_short,
                                    old_hand, new_hand, role);
    }
}
static void log_mac_changed(const uint8_t *old_address, const uint8_t *new_address)
{
    log3(3u, 0x265u, old_high, 0x0cc00000u, old_high_short,
         old_address[5], old_address[4], old_address[3]);
    log3(3u, 0x269u, old_low, 0x0cc00000u, old_low_short,
         old_address[2], old_address[1], old_address[0]);
    log3(3u, 0x26du, new_high, 0x0cc00000u, new_high_short,
         new_address[5], new_address[4], new_address[3]);
    log3(3u, 0x271u, new_low, 0x0cc00000u, new_low_short,
         new_address[2], new_address[1], new_address[0]);
}
static void log_mac_size(uint32_t line, int16_t size)
{
    if (size == 0)
        log0(4u, line, absent, 0x10000000u, absent_short);
    else
        log1(2u, line, bad_size, 0x08400000u, bad_size_short, (uint32_t)(int32_t)size);
}

void audio_setting_dispatch_type11_467540(const uint8_t *data)
{
    if (data == 0) {
        log0(2u, 0x233u, null_message, 0x08000000u, null_short);
        return;
    }
    uint8_t *record = audio_setting_unit_record_get_466010();
    const uint8_t desired = data[0];
    const int16_t mac_size = (int16_t)(data[4] | (uint16_t)(data[5] << 8));
    const uint8_t *new_address = data + 6u;
    log2(3u, 0x23cu, received, 0x0c800000u, received_short,
         desired, (uint32_t)(int32_t)mac_size);
    const uint8_t previous = record[11];
    uint32_t mac_changed = 0u;
    if (mac_size == 6)
        mac_changed = g2_lfs_memcmp(record + 12u, new_address, 6u) != 0;
    if (mac_changed != 0u)
        log_mac_changed(record + 12u, new_address);
    log_policy(previous, desired);
    const uint8_t outcome = (uint8_t)audio_ring_connect_policy_on_hand_49f15a(previous, desired);
    uint32_t connect_delay = 4000u;
    if (mac_changed != 0u && audio_ring_address_is_unset_4a26e8(record + 12u) != 0u) {
        connect_delay = 8000u;
        log1(3u, 0x281u, recovered, 0x0c400000u, recovered_short, 8000u);
    }
    if (outcome == 2u) {
        log1(2u, 0x2a6u, rejected, 0x08400000u, rejected_short, previous);
        return;
    }
    if (outcome != 0u && outcome >= 2u)
        return;
    record[11] = desired;
    if (mac_size == 6) {
        (void)audio_queue_copy_bytes(record + 12u, new_address, 6u);
        log6(outcome == 0u ? 0x286u : 0x293u, record + 12u);
    } else {
        log_mac_size(outcome == 0u ? 0x286u : 0x293u, mac_size);
    }
    audio_ble_master_set_target_hand_4a2068(record + 12u, 0, 0u);
    audio_uart_ring_unpair_publish_hand_4661a6();
    if (mac_changed != 0u)
        audio_uart_ring_unpair_commit_hand_466016();
    if (outcome == 0u) {
        audio_ble_master_hand_changed_4a2948(desired, connect_delay, 0u);
        if (audio_uart_device_role_get() == 1u)
            audio_ble_status_reply(1u);
    } else {
        const char *kind = mac_changed != 0u ? ", ring mac changed" : " only";
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(3u, module, path, function, 0x29au, unchanged, kind);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x0c400000u, unchanged_short, unchanged_short, kind);
        audio_ble_master_hand_changed_4a2948(desired, 0u, mac_changed ^ 1u);
        if (mac_changed != 0u && audio_uart_device_role_get() == 1u)
            audio_ble_status_reply(1u);
    }
}
