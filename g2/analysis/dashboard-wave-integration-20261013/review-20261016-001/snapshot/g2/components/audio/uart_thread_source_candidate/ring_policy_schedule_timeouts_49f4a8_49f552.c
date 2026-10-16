/* Stock RING_ConnectPolicyScheduleConnectTimeout at 0x49f4a8 and
 * RING_ConnectPolicyScheduleReconnectTimeout at 0x49f552. */
#include <stdint.h>

extern volatile uint8_t audio_ble_ring_policy_pending_2007500b;
extern void audio_ble_ring_policy_delayed(void);
extern uint32_t audio_ble_master_success_delayed(uint32_t);
extern void audio_event_loop_remove_delayed(void (*)(void));
extern void audio_event_loop_push_delayed(void (*)(void), uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "ring.policy";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\ring_service\\ring_connect_policy.c";
static const char connect_function[] = "RING_ConnectPolicyScheduleConnectTimeout";
static const char reconnect_function[] = "RING_ConnectPolicyScheduleReconnectTimeout";
static const char connect_message[] = "[RingPolicy] schedule connect timeout notify in %ums";
static const char connect_short[] = "[ring.policy][RingPolicy] schedule connect timeout notify in %ums";
static const char reconnect_message[] = "[RingPolicy] schedule reconnect timeout notify in %ums";
static const char reconnect_short[] = "[ring.policy][RingPolicy] schedule reconnect timeout notify in %ums";
static const char pending_message[] = "[RingPolicy] reconnect timeout already pending, keep current %ums";
static const char pending_short[] = "[ring.policy][RingPolicy] reconnect timeout already pending, keep current %ums";

void audio_ble_ring_policy_schedule_connect_timeout_49f4a8(void)
{
    audio_event_loop_remove_delayed((void (*)(void))audio_ble_master_success_delayed);
    audio_event_loop_push_delayed((void (*)(void))audio_ble_master_success_delayed,
                                  0x5au, 20000u);
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, connect_function, 0xbcu,
                           connect_message, 20000u);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0c400000u,
                                    connect_short, connect_short, 20000u);
}

void audio_ble_ring_policy_schedule_reconnect_timeout_49f552(void)
{
    if (audio_ble_ring_policy_pending_2007500b == 0u) {
        audio_ble_ring_policy_pending_2007500b = 1u;
        audio_event_loop_remove_delayed(audio_ble_ring_policy_delayed);
        audio_event_loop_push_delayed(audio_ble_ring_policy_delayed, 0u, 20000u);
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(3u, module, path, reconnect_function, 0xd9u,
                               reconnect_message, 20000u);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x0c400000u,
                                        reconnect_short, reconnect_short, 20000u);
    } else {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(4u, module, path, reconnect_function, 0xd3u,
                               pending_message, 20000u);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x10400000u,
                                        pending_short, pending_short, 20000u);
    }
}
