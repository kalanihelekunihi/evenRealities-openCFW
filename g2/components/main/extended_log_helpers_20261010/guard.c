#include <stdint.h>

#define LOG_BASE ((volatile uint8_t *)(uintptr_t)0x20070be8u)
typedef struct {
    void (*enter)(void);
    void (*exit)(void);
} g2_log_guard_provider;

/* Stock 0x43d416..0x43d438. */
void g2_log_candidate_guard_enter(void *context)
{
    const g2_log_guard_provider *p = (const g2_log_guard_provider *)context;
    if (LOG_BASE[242] != 0u) {
        p->enter();
        LOG_BASE[244] = 1u;
    } else {
        LOG_BASE[243] = 1u;
    }
}

/* Stock 0x43d438..0x43d45a. */
void g2_log_candidate_guard_exit(void *context)
{
    const g2_log_guard_provider *p = (const g2_log_guard_provider *)context;
    if (LOG_BASE[242] != 0u) {
        p->exit();
        LOG_BASE[244] = 0u;
    } else {
        LOG_BASE[243] = 0u;
    }
}
