#include <stdint.h>

#define DB_BASE ((volatile g2_db_row *)(uintptr_t)0x200708ecu)
#define DB_CONFIG (*(volatile uint32_t *)(uintptr_t)0x200004b8u)
#define DB_TIMER_ACTIVE (*(volatile uint8_t *)(uintptr_t)0x200709e9u)
#define DB_TIMER_WORD 0x200709dcu

typedef struct {
    uint8_t pad0[7];
    uint8_t active;
    uint16_t count;
    uint8_t pad1[2];
    uint32_t remaining;
    uint32_t interval;
    uint32_t expiry;
} g2_db_row;

typedef struct {
    void (*start_timer)(uint32_t timer_word, uint32_t milliseconds);
} g2_db_provider;

static uint32_t in_use(volatile g2_db_row *row)
{
    return row->active != 0u || row->remaining != 0u || row->count != 0u;
}

static uint32_t take_second(uint32_t value)
{
    return value >= 1001u ? value - 1000u : 0u;
}

/* Stock 0x542960..0x5429f2; lower timer provider is explicit. */
void g2_smp_candidate_db_service(void *context)
{
    const g2_db_provider *provider = (const g2_db_provider *)context;
    volatile g2_db_row *row = DB_BASE;
    for (uint32_t i = 0; i < 10u; ++i, ++row) {
        if (!in_use(row)) continue;
        row->interval = take_second(row->interval);
        row->remaining = take_second(row->remaining);
        row->expiry = take_second(row->expiry);
        if (row->interval == 0u) {
            uint32_t config = DB_CONFIG;
            uint32_t divisor = *(volatile uint16_t *)(uintptr_t)(config + 20u);
            row->count = divisor == 0u ? 0u : (uint16_t)(row->count / divisor);
            if (row->count != 0u)
                row->interval = *(volatile uint32_t *)(uintptr_t)(config + 16u);
        }
        if (row->expiry == 0u) row->active = 0u;
        if (in_use(row) && DB_TIMER_ACTIVE == 0u)
            provider->start_timer(DB_TIMER_WORD, 1000u);
    }
}
