/* Stock RING_ConnectPolicyCancelConnectTimeout, 0x49f5f8..0x49f646. */
#include <stdint.h>

extern volatile uint8_t audio_ble_ring_policy_pending_2007500b;
extern void audio_ble_ring_policy_delayed(void);
extern uint32_t audio_ble_master_success_delayed(uint32_t);
extern void audio_event_loop_remove_delayed(void (*)(void));
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "ring.policy";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\ring_service\\ring_connect_policy.c";
static const char function[] = "RING_ConnectPolicyCancelConnectTimeout";
static const char message[] = "[RingPolicy] cancel connect timeout notify";
static const char compact[] = "[ring.policy][RingPolicy] cancel connect timeout notify";

void audio_ble_ring_policy_cancel_connect_timeout_49f5f8(void)
{
    audio_ble_ring_policy_pending_2007500b = 0u;
    audio_event_loop_remove_delayed(audio_ble_ring_policy_delayed);
    audio_event_loop_remove_delayed((void (*)(void))audio_ble_master_success_delayed);
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, 0xe1u, message);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0c000000u, compact, compact);
}
