/* Stock _GetState, 0x49f05c..0x49f0da. */
#include <stdint.h>

extern uint8_t audio_ble_ring_policy_state_2007408c[];
extern uint32_t audio_ble_ring_policy_tick_now(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "ring.policy";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\ring_service\\ring_connect_policy.c";
static const char function[] = "_GetState";
static const char timeout_message[] = "[RingPolicy] state %d timeout, back to IDLE";
static const char timeout_short[] = "[ring.policy][RingPolicy] state %d timeout, back to IDLE";

uint32_t audio_ble_ring_policy_get_state_49f05c(void)
{
    uint8_t *const record = audio_ble_ring_policy_state_2007408c;
    const uint8_t state = record[0];
    if (state != 0u) {
        uint32_t timeout = 0u;
        if (state == 1u) timeout = 20000u;
        else if (state == 2u) timeout = 3000u;
        if (timeout != 0u) {
            const uint32_t start = (uint32_t)record[4] |
                                   ((uint32_t)record[5] << 8u) |
                                   ((uint32_t)record[6] << 16u) |
                                   ((uint32_t)record[7] << 24u);
            const uint32_t elapsed = start == 0u ? UINT32_MAX :
                                     audio_ble_ring_policy_tick_now() - start;
            if (elapsed >= timeout) {
                if ((audio_log_flags() & 2u) != 0u)
                    audio_log_extended(4u, module, path, function, 0x56u,
                                       timeout_message, state);
                if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
                    (void)compressed_log_output(0x10400000u,
                                                timeout_short, timeout_short, state);
                record[0] = 0u;
                record[4] = 0u; record[5] = 0u; record[6] = 0u;
                record[7] = 0u; record[8] = 0u;
            }
        }
    }
    return record[0];
}
