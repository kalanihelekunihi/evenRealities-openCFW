#include <stdint.h>
#include "onebit.h"

#define STATE ((volatile uint8_t *)(uintptr_t)0x20070be8u)
#define BUFFER ((uint8_t *)(uintptr_t)0x2006bd30u)

typedef struct {
    void (*guard_enter)(void);
    void (*guard_exit)(void);
} g2_log_policy_providers;

uint32_t g2_log_candidate_append_normal(uint32_t, uint8_t *, const uint8_t *);
uint32_t g2_log_candidate_module_length(const uint8_t *);
uint32_t g2_log_candidate_postformat(const void *, uint32_t, uint32_t,
                                     uint32_t, uint32_t);
uint32_t g2_log_candidate_timestamp_5(uint8_t *, uint32_t);
uint32_t g2_log_candidate_module_policy(const g2_log_policy_providers *,
                                        uint32_t);

static uint32_t append(uint32_t offset, const uint8_t *source)
{
    return offset + g2_log_candidate_append_normal(offset, BUFFER + offset,
                                                    source);
}

/* Entry-to-return normal-level SMP logger for category masks. Precondition:
 * non-null module, valid source strings and initialized table pointers.
 * Color, module policy and input/output token filters may vary. */
void g2_log_candidate_smp_onebit(const g2_log_onebit_providers *p,
                                 uint32_t level, uint32_t module_word,
                                 uint32_t file_word, uint32_t function_word,
                                 uint32_t line, uint32_t format_word,
                                 uint32_t arguments_word)
{
    uint32_t lv = (uint8_t)level;
    if (STATE[241] == 0u || STATE[0] < lv || lv > 5u) return;
    const uint8_t *module = (const uint8_t *)(uintptr_t)module_word;
    g2_log_policy_providers policy = {p->guard_enter, p->guard_exit};
    if (g2_log_candidate_module_policy(&policy,module_word) < lv) return;
    if (p->find_token(module_word,(uint32_t)(uintptr_t)(STATE+1u))==0u)
        return;
    uint32_t offset = 0u;
    p->guard_enter();
    if (STATE[245] != 0u) {
        offset = append(offset, (const uint8_t *)(uintptr_t)0x0043d978u);
        uint32_t table = *(volatile uint32_t *)(uintptr_t)(0x2000098cu + lv * 4u);
        offset = append(offset, (const uint8_t *)(uintptr_t)table);
    }
    uint32_t mask = *(volatile uint32_t *)(uintptr_t)
        (0x20070be8u + 216u + lv * 4u);
    if ((mask & 1u) != 0u) {
        uint32_t table = *(volatile uint32_t *)(uintptr_t)(0x20000974u + lv * 4u);
        offset = append(offset, (const uint8_t *)(uintptr_t)table);
    }
    if ((mask & 2u) != 0u) {
        offset = append(offset, module);
        uint32_t length = g2_log_candidate_module_length(module);
        if (length < 16u) {
            uint8_t spaces[16];
            for (uint32_t i=0;i<15u-length;i++) spaces[i]=' ';
            spaces[15u-length]=0u;
            offset=append(offset,spaces);
        }
        offset=append(offset,(const uint8_t *)(uintptr_t)0x0043d9e8u);
    }
    if ((mask & (4u|8u|16u)) != 0u) {
        offset=append(offset,(const uint8_t *)(uintptr_t)0x0043d9ecu);
        if ((mask&4u)!=0u) {
            offset=append(offset,(const uint8_t *)(uintptr_t)p->date());
            if ((mask&(8u|16u))!=0u)
                offset=append(offset,(const uint8_t *)(uintptr_t)0x0043d9e8u);
        }
        if ((mask&8u)!=0u) {
            offset=append(offset,(const uint8_t *)(uintptr_t)p->time());
            if ((mask&16u)!=0u)
                offset=append(offset,(const uint8_t *)(uintptr_t)0x0043d9e8u);
        }
        if ((mask&16u)!=0u) offset=append(offset,(const uint8_t *)(uintptr_t)p->tick());
        offset=append(offset,(const uint8_t *)(uintptr_t)0x0043da60u);
    }
    if ((mask & (32u|64u|128u)) != 0u) {
        offset=append(offset,(const uint8_t *)(uintptr_t)0x0043da64u);
        if ((mask&32u)!=0u) {
            offset=append(offset,(const uint8_t *)(uintptr_t)file_word);
            if ((mask&64u)!=0u)
                offset=append(offset,(const uint8_t *)(uintptr_t)0x0043da68u);
            else if ((mask&128u)!=0u)
                offset=append(offset,(const uint8_t *)(uintptr_t)0x0043d9e8u);
        }
        if ((mask&128u)!=0u) {
            uint8_t number[5];
            (void)g2_log_candidate_timestamp_5(number,line);
            offset=append(offset,number);
            if ((mask&64u)!=0u)
                offset=append(offset,(const uint8_t *)(uintptr_t)0x0043d9e8u);
        }
        if ((mask&64u)!=0u) offset=append(offset,(const uint8_t *)(uintptr_t)function_word);
        offset=append(offset,(const uint8_t *)(uintptr_t)0x0043da74u);
    }
    (void)g2_log_candidate_postformat(p,lv,offset,format_word,arguments_word);
}
