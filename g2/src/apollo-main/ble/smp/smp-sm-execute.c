#include <stdint.h>

#define SMP_BASE ((volatile uint8_t *)(uintptr_t)0x20070aecu)
#define MOD 0x0078e6ccu
#define TAG 0x56f148u
#define REQ 0x56f144u
#define CHI 0x56f14cu
#define ALT 0x0078e6c4u
#define FILE_ID 0x006e1994u
#define FORMAT 0x0077bf14u
#define RAW_FORMAT 0x00765710u
#define TRACE_AUX 0x00789060u

typedef struct {
    uint32_t (*conn_role)(uint32_t);
    uint32_t (*log_gate)(void);
    uint32_t (*compare)(uint32_t, uint32_t, uint32_t);
    uint32_t (*log_flags)(void);
    uint32_t (*state_name)(uint32_t);
    uint32_t (*event_name)(uint32_t);
    void (*extended_log)(uint32_t, uint32_t, uint32_t, uint32_t,
                         uint32_t, uint32_t, uint32_t, uint32_t);
    void (*trace)(uint32_t, uint32_t, uint32_t, uint32_t);
} g2_smp_execute_providers;

void g2_smp_candidate_dispatch_tail(void *, uint32_t, uint32_t);

/* Stock smpSmExecute at 0x56ee62..0x56f144. Providers are the eight
 * separately linked callees; the source owns the complete local control flow.
 */
void g2_smp_candidate_execute(void *context, uint32_t ccb_word,
                              uint32_t message_word)
{
    const g2_smp_execute_providers *p = context;
    volatile uint8_t *ccb = (volatile uint8_t *)(uintptr_t)ccb_word;
    volatile uint8_t *msg = (volatile uint8_t *)(uintptr_t)message_word;
    uint32_t enabled = 0u;
    if (SMP_BASE[248] != 0u) {
        uint32_t config_word = *(volatile uint32_t *)(ccb_word + 72u);
        if (config_word != 0u &&
            *(volatile uint8_t *)(uintptr_t)config_word != 0u) enabled = 1u;
    }

    for (uint32_t level = 1; level <= 4; level++) {
        if (p->log_gate() == 0u) continue;
        uint32_t accepted = level == 1u
            ? p->compare(MOD, REQ, 3u) == 0u
            : level == 2u
              ? p->compare(MOD, ALT, 4u) == 0u
              : level == 3u
                ? p->compare(MOD, MOD, 4u) == 0u
                : 1u;
        if (!accepted) continue;
        if ((p->log_flags() & 2u) != 0u) {
            uint32_t state = ccb[62], event = msg[2];
            if (enabled) {
                state = p->state_name(state);
                event = p->event_name(event);
            }
            p->extended_log(level, TAG, FILE_ID, TRACE_AUX,
                            enabled ? 852u : 855u,
                            enabled ? FORMAT : RAW_FORMAT, event, state);
        }
        goto dispatch;
    }
    if (p->log_gate() == 0u || p->compare(TAG, CHI, 3u) != 0u) {
        uint32_t state = ccb[62], event = msg[2];
        if (enabled) {
            state = p->state_name(state);
            event = p->event_name(event);
        }
        p->trace(MOD, enabled ? FORMAT : RAW_FORMAT, event, state);
    }
dispatch:
    g2_smp_candidate_dispatch_tail(context, ccb_word, message_word);
}
