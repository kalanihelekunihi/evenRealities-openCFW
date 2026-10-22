/* Ring connect policy, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\protocols\ring_service\ring_connect_policy.c.
 * Native 0x49f028..0x49f05c (tick helpers) and 0x49f326..0x49f4a8,
 * 0x49f702..0x49f744 (RING_CONNECT_INFO throttle); literal pool 0x49f744..0x49f828.
 *
 * Policy record at RAM 0x2007408c: +0 state (0 IDLE, 1 SWITCH window 20 s,
 * 2 FOLLOWUP 3 s), +4 state entry tick, +8 "first RING_CONNECT_INFO allowed in
 * the switch window" flag. RAM 0x200748fc holds the tick at which the last
 * RING_CONNECT_INFO was processed (0 = never; a real tick of 0 is stored as 1).
 *
 * _ring_policy_tick_now 0x49f020, _GetState 0x49f05c, _EnterState 0x49f0da,
 * _ringReconnectTimeoutFire 0x49f500 and RING_ConnectPolicyReset 0x49f6ae are
 * implemented in ble/ble-ring, ble/ble-pair and drivers/peripherals/ring-policy. */
#include <stdint.h>
#include <stdbool.h>

#define RING_POLICY_SWITCH_WINDOW_MS 20000u
#define RING_POLICY_FOLLOWUP_MS 3000u
#define RING_POLICY_STATE_SWITCH 1u
#define RING_POLICY_STATE_FOLLOWUP 2u
#define RING_POLICY_FIRST_INFO_SEEN 8u /* byte offset in the policy record */

extern uint8_t audio_ble_ring_policy_state_2007408c[];      /* RAM 0x2007408c policy record */
extern uint32_t audio_ble_ring_policy_deadline_200748fc;    /* RAM 0x200748fc last processed tick */

extern uint32_t audio_ble_ring_policy_tick_now(void);       /* _ring_policy_tick_now 0x49f020 */
extern uint32_t audio_ble_ring_policy_get_state_49f05c(void); /* _GetState 0x49f05c */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "ring.policy"; /* ROM 0x78bd98 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\ring_service\\ring_connect_policy.c"; /* ROM 0x6e15fc */
static const char should_block_fn[] = "RING_ConnectPolicyShouldBlockRingConnectInfo"; /* ROM 0x7379f4 */
static const char allow_first[] = "[RingPolicy] allow first RING_CONNECT_INFO in switch window"; /* ROM 0x7180b8 */
static const char allow_first_short[] =
    "[ring.policy][RingPolicy] allow first RING_CONNECT_INFO in switch window"; /* ROM 0x6f5a80 */
static const char block_window[] = "[RingPolicy] block RING_CONNECT_INFO: switch window active"; /* ROM 0x7180f4 */
static const char block_window_short[] =
    "[ring.policy][RingPolicy] block RING_CONNECT_INFO: switch window active"; /* ROM 0x6fc89c */
static const char block_recent[] = "[RingPolicy] block RING_CONNECT_INFO: last processed within %ums"; /* ROM 0x705094 */
static const char block_recent_short[] =
    "[ring.policy][RingPolicy] block RING_CONNECT_INFO: last processed within %ums"; /* ROM 0x6ef638 */
static const char mark_fn[] = "RING_ConnectPolicyMarkRingConnectInfoProcessed"; /* ROM 0x737a24 */
static const char mark_message[] = "[RingPolicy] mark RING_CONNECT_INFO processed at %lu"; /* ROM 0x7220e8 */
static const char mark_short[] = "[ring.policy][RingPolicy] mark RING_CONNECT_INFO processed at %lu"; /* ROM 0x7050d8 */
static const char throttle_fn[] = "RING_ConnectPolicyResetRingConnectInfoThrottle"; /* ROM 0x737a54 */
static const char throttle_message[] =
    "[RingPolicy] reset RING_CONNECT_INFO throttle (keep dominant_hand state)"; /* ROM 0x6f5b18 */
static const char throttle_short[] =
    "[ring.policy][RingPolicy] reset RING_CONNECT_INFO throttle (keep dominant_hand state)"; /* ROM 0x6e4a60 */

#define LOG_EXT_ON() ((audio_log_flags() & 2u) != 0u)
#define LOG_CMP_ON() ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)

/* Ticks since `since`; 0 means "never" and reads as UINT32_MAX. */
uint32_t _ring_policy_elapsed_ticks(uint32_t since)
{
    if (since == 0u)
        return UINT32_MAX;
    return audio_ble_ring_policy_tick_now() - since;
}

uint32_t _ring_policy_timeout_for_mode(uint8_t state)
{
    if (state == RING_POLICY_STATE_SWITCH)
        return RING_POLICY_SWITCH_WINDOW_MS;
    if (state == RING_POLICY_STATE_FOLLOWUP)
        return RING_POLICY_FOLLOWUP_MS;
    return 0u;
}

/* In the switch window the first RING_CONNECT_INFO passes and later ones are
 * blocked; outside it, one processed within 20 s blocks the next. */
bool RING_ConnectPolicyShouldBlockRingConnectInfo(bool is_ring_connect_info)
{
    if (!is_ring_connect_info)
        return false;
    if (audio_ble_ring_policy_get_state_49f05c() == RING_POLICY_STATE_SWITCH) {
        if (audio_ble_ring_policy_state_2007408c[RING_POLICY_FIRST_INFO_SEEN] == 0u) {
            if (LOG_EXT_ON())
                audio_log_extended(3u, module_tag, source_file, should_block_fn, 0x95u, allow_first);
            if (LOG_CMP_ON())
                (void)compress_log_output(0x0c000000u, allow_first_short, allow_first_short);
            return false;
        }
        if (LOG_EXT_ON())
            audio_log_extended(2u, module_tag, source_file, should_block_fn, 0x98u, block_window);
        if (LOG_CMP_ON())
            (void)compress_log_output(0x08000000u, block_window_short, block_window_short);
        return true;
    }
    if (audio_ble_ring_policy_deadline_200748fc == 0u ||
        _ring_policy_elapsed_ticks(audio_ble_ring_policy_deadline_200748fc) >= RING_POLICY_SWITCH_WINDOW_MS)
        return false;
    if (LOG_EXT_ON())
        audio_log_extended(2u, module_tag, source_file, should_block_fn, 0xa0u, block_recent,
                           RING_POLICY_SWITCH_WINDOW_MS);
    if (LOG_CMP_ON())
        (void)compress_log_output(0x08400000u, block_recent_short, block_recent_short,
                                  RING_POLICY_SWITCH_WINDOW_MS);
    return true;
}

void RING_ConnectPolicyMarkRingConnectInfoProcessed(bool processed)
{
    if (!processed)
        return;
    audio_ble_ring_policy_deadline_200748fc = audio_ble_ring_policy_tick_now();
    if (audio_ble_ring_policy_deadline_200748fc == 0u)
        audio_ble_ring_policy_deadline_200748fc = 1u;
    if (audio_ble_ring_policy_get_state_49f05c() == RING_POLICY_STATE_SWITCH)
        audio_ble_ring_policy_state_2007408c[RING_POLICY_FIRST_INFO_SEEN] = 1u;
    if (LOG_EXT_ON())
        audio_log_extended(3u, module_tag, source_file, mark_fn, 0xb3u, mark_message,
                           audio_ble_ring_policy_deadline_200748fc);
    if (LOG_CMP_ON())
        (void)compress_log_output(0x0c400000u, mark_short, mark_short,
                                  audio_ble_ring_policy_deadline_200748fc);
}

void RING_ConnectPolicyResetRingConnectInfoThrottle(void)
{
    if (LOG_EXT_ON())
        audio_log_extended(3u, module_tag, source_file, throttle_fn, 0xffu, throttle_message);
    if (LOG_CMP_ON())
        (void)compress_log_output(0x0c000000u, throttle_short, throttle_short);
    audio_ble_ring_policy_deadline_200748fc = 0u;
}
