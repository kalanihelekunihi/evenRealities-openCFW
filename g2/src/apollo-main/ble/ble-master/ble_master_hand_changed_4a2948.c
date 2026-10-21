/* Stock APP_MasterOnDominantHandChangedEx, 0x4a2948..0x4a2c6a. */
#include <stdint.h>

extern uint32_t audio_uart_ring_active(void);
extern uint32_t audio_ble_peer_ring_status_47d8f0(void);
extern const char *audio_ble_ring_link_state_name(uint8_t);
extern volatile uint8_t audio_ble_ring_link_state;
extern volatile uint8_t audio_ble_master_open_connection;
extern uint8_t *audio_ble_master_context;
extern uint8_t *audio_setting_unit_record_get_466010(void);
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t);
extern uint32_t audio_ring_address_is_unset_4a26e8(const uint8_t *);
extern uint32_t audio_ble_master_link_matches_target(const uint8_t *);
extern void audio_ble_master_set_target_hand_4a2068(const void *, const void *, uint32_t);
extern uint32_t audio_ble_master_auth_mode_set(uint8_t);
extern void audio_ble_master_reset_retry_count(void);
extern void audio_ble_master_clear_failure_notify(void);
extern void audio_ble_master_begin_failure_notify_4a1546(void);
extern void audio_ble_master_reset_scene_pending_4a2658(void);
extern void audio_ble_master_schedule_connect(uint32_t, uint8_t);
extern void audio_ble_master_disconnect_delayed(uint32_t);
extern void audio_ble_master_connect_event(void);
extern void audio_ble_master_start_try_connect_ring(void);
extern void audio_ble_ring_policy_schedule_connect_timeout_49f4a8(void);
extern void audio_ble_ring_policy_schedule_reconnect_timeout_49f552(void);
extern void audio_ble_ring_policy_cancel_connect_timeout_49f5f8(void);
extern void audio_ble_ring_policy_notify_success_49f646(void);
extern void audio_ble_set_ring_link_state(uint8_t, const char *);
extern void audio_event_loop_remove_delayed(void (*)(void));
extern void audio_event_loop_push_delayed(void (*)(void), uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "ble.master";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_central.c";
static const char function[] = "APP_MasterOnDominantHandChangedEx";
static const char status_message[] = "[RingSwitch] dominant_hand=%u owner=%d state=%s peerRing=%u connectDelay=%lu";
static const char status_short[] = "[ble.master][RingSwitch] dominant_hand=%u owner=%d state=%s peerRing=%u connectDelay=%lu";
static const char no_mac[] = "[RingSwitch] owner no stored ring mac, skip connect";
static const char no_mac_short[] = "[ble.master][RingSwitch] owner no stored ring mac, skip connect";
static const char already[] = "[RingSwitch] owner already connected";
static const char already_short[] = "[ble.master][RingSwitch] owner already connected";
static const char start[] = "[RingSwitch] owner start connect by dominant_hand%s";
static const char start_short[] = "[ble.master][RingSwitch] owner start connect by dominant_hand%s";
static const char silent_suffix[] = " (silent, 20s timeout report)";
static const char cancel[] = "[RingSwitch] non-owner cancel opening connId=%d";
static const char cancel_short[] = "[ble.master][RingSwitch] non-owner cancel opening connId=%d";
static const char disconnect[] = "[RingSwitch] non-owner silent disconnect local ring";
static const char disconnect_short[] = "[ble.master][RingSwitch] non-owner silent disconnect local ring";
static const char disconnect_reason[] = "dominant_hand non-owner disconnect";
static const char idle_reason[] = "dominant_hand non-owner idle";
static const uint8_t target_name_prefix[14] = {
    'E', 'V', 'E', 'N', ' ', 'R', '1', 0, 'r', 'i', 'n', 'g', 'M', 'a'
};

static void log0(uint8_t severity, uint32_t line, const char *message,
                 uint32_t level, const char *compact)
{
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(severity, module, path, function, line, message);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(level, compact, compact);
}
static void log1(uint8_t severity, uint32_t line, const char *message,
                 uint32_t level, const char *compact, uint32_t value)
{
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(severity, module, path, function, line, message, value);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(level, compact, compact, value);
}

void audio_ble_master_hand_changed_4a2948(uint32_t desired,
                                            uint32_t delay,
                                            uint32_t silent,
                                            uint32_t detail)
{
    (void)detail;
    const uint8_t owner = (uint8_t)audio_uart_ring_active();
    if ((audio_log_flags() & 2u) != 0u) {
        const uint32_t peer = audio_ble_peer_ring_status_47d8f0();
        const char *state = audio_ble_ring_link_state_name(audio_ble_ring_link_state);
        audio_log_extended(3u, module, path, function, 0x574u,
                           status_message, (uint8_t)desired, owner, state, peer, delay);
    }
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u) {
        const uint32_t peer = audio_ble_peer_ring_status_47d8f0();
        const char *state = audio_ble_ring_link_state_name(audio_ble_ring_link_state);
        (void)compressed_log_output(0x0d400000u, status_short, status_short,
                                    (uint8_t)desired, owner, state, peer, delay);
    }
    if (owner != 0u) {
        uint8_t address[8];
        (void)audio_queue_copy_bytes(address,
                                     audio_setting_unit_record_get_466010() + 12u, 6u);
        if (audio_ring_address_is_unset_4a26e8(address) != 0u) {
            log0(2u, 0x579u, no_mac, 0x08000000u, no_mac_short);
            return;
        }
        if (audio_ble_master_link_matches_target(address) != 0u) {
            log0(3u, 0x57eu, already, 0x0c000000u, already_short);
            audio_ble_master_clear_failure_notify();
            audio_ble_ring_policy_notify_success_49f646();
            return;
        }
        uint8_t name[15];
        (void)audio_queue_copy_bytes(name, target_name_prefix, 14u);
        name[14] = 0u;
        audio_ble_master_set_target_hand_4a2068(address, name, 15u);
        (void)audio_ble_master_auth_mode_set(1u);
        audio_ble_master_reset_retry_count();
        if ((uint8_t)silent == 0u) {
            audio_ble_master_begin_failure_notify_4a1546();
            audio_ble_ring_policy_schedule_connect_timeout_49f4a8();
        } else {
            audio_ble_ring_policy_schedule_reconnect_timeout_49f552();
        }
        audio_ble_master_schedule_connect(delay, (uint8_t)silent);
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(3u, module, path, function, 0x596u, start,
                               (uint8_t)silent == 0u ? "" : silent_suffix);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x0c400000u, start_short, start_short,
                                        (uint8_t)silent == 0u ? "" : silent_suffix);
        return;
    }
    (void)audio_ble_master_auth_mode_set(0u);
    audio_event_loop_remove_delayed(audio_ble_master_connect_event);
    audio_event_loop_remove_delayed(audio_ble_master_start_try_connect_ring);
    audio_ble_master_reset_retry_count();
    audio_ble_master_clear_failure_notify();
    audio_ble_master_reset_scene_pending_4a2658();
    audio_ble_ring_policy_cancel_connect_timeout_49f5f8();
    if (audio_ble_ring_link_state == 1u && audio_ble_master_open_connection != 0u) {
        log1(3u, 0x5a4u, cancel, 0x0c400000u, cancel_short,
             audio_ble_master_open_connection);
        audio_ble_master_disconnect_delayed(audio_ble_master_open_connection);
    } else if (audio_ble_master_context == 0 ||
               audio_ble_master_context[0x55u] == 0u) {
        audio_ble_set_ring_link_state(0u, idle_reason);
    } else {
        log0(3u, 0x5a7u, disconnect, 0x0c000000u, disconnect_short);
        audio_ble_set_ring_link_state(4u, disconnect_reason);
        audio_event_loop_push_delayed(audio_ble_master_connect_event, 0x102u, 0u);
    }
}
