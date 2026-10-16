/* Stock RING_ConnectPolicyOnDominantHand, 0x49f15a..0x49f326. */
#include <stdint.h>

extern uint32_t audio_ble_ring_policy_get_state_49f05c(void);
extern void audio_ble_ring_policy_enter_state(uint8_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "ring.policy";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\ring_service\\ring_connect_policy.c";
static const char function[] = "RING_ConnectPolicyOnDominantHand";
static const char status_message[] = "[RingPolicy] dominant_hand cur=%u new=%u state=%d";
static const char status_short[] = "[ring.policy][RingPolicy] dominant_hand cur=%u new=%u state=%d";
static const char same_window[] = "[RingPolicy] dominant_hand UNCHANGED within switch window, keep window";
static const char same_window_short[] = "[ring.policy][RingPolicy] dominant_hand UNCHANGED within switch window, keep window";
static const char same_followup[] = "[RingPolicy] dominant_hand UNCHANGED, enter FOLLOWUP";
static const char same_followup_short[] = "[ring.policy][RingPolicy] dominant_hand UNCHANGED, enter FOLLOWUP";
static const char rejected[] = "[RingPolicy] dominant_hand REJECTED within %ums switch window";
static const char rejected_short[] = "[ring.policy][RingPolicy] dominant_hand REJECTED within %ums switch window";
static const char accepted[] = "[RingPolicy] dominant_hand ACCEPTED, %u -> %u, open switch window";
static const char accepted_short[] = "[ring.policy][RingPolicy] dominant_hand ACCEPTED, %u -> %u, open switch window";

static void log0(uint32_t line, const char *message, const char *compact)
{
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, line, message);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0c000000u, compact, compact);
}

uint32_t audio_ring_connect_policy_on_hand_49f15a(uint32_t previous,
                                                    uint32_t desired,
                                                    uint32_t ignored,
                                                    uint32_t detail)
{
    (void)ignored;
    const uint8_t old_hand = (uint8_t)previous;
    const uint8_t new_hand = (uint8_t)desired;
    const uint8_t state = (uint8_t)audio_ble_ring_policy_get_state_49f05c();
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, 0x70u, status_message,
                           old_hand, new_hand, state, detail);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0cc00000u, status_short, status_short,
                                    old_hand, new_hand, state);
    if (new_hand == old_hand) {
        if (state == 1u) {
            log0(0x7au, same_window, same_window_short);
        } else {
            audio_ble_ring_policy_enter_state(2u);
            log0(0x78u, same_followup, same_followup_short);
        }
        return 1u;
    }
    if (state == 1u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, function, 0x82u, rejected, 20000u);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x08400000u, rejected_short, rejected_short, 20000u);
        return 2u;
    }
    audio_ble_ring_policy_enter_state(1u);
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, 0x88u, accepted,
                           old_hand, new_hand);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0c800000u, accepted_short, accepted_short,
                                    old_hand, new_hand);
    return 0u;
}
