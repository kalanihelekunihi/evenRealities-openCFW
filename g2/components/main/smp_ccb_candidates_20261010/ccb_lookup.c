#include <stdint.h>

typedef struct {
    uint32_t ccb_base;
    uint32_t category, category_alt, source, function, file;
    uint32_t err_text, smp_text, hci_text;
    uint32_t (*log_gate)(uint32_t carry);
    uint32_t (*compare)(uint32_t lhs, uint32_t rhs, uint32_t length);
    uint32_t (*log_flags)(void);
    void (*log_extended)(uint32_t level, uint32_t format, uint32_t source,
                         uint32_t file, uint32_t line, uint32_t function,
                         uint32_t conn_id);
    void (*trace)(uint32_t category, uint32_t function, uint32_t conn_id);
} g2_smp_ccb_provider;

/* Stock 0x5375fc..0x537742. The original accepts nonzero low-byte IDs
 * without an upper-bound check; this C preserves that arithmetic. */
uint32_t g2_smp_candidate_ccb_by_id(void *context, uint8_t conn_id)
{
    const g2_smp_ccb_provider *p = (const g2_smp_ccb_provider *)context;
    uint32_t id = conn_id;
    if (id != 0u) return p->ccb_base + (id - 1u) * 76u;

    uint32_t carry = id;
    for (uint32_t level = 1u; level <= 4u; ++level) {
        carry = p->log_gate(carry);
        if (carry == 0u) continue;
        if (level < 4u) {
            uint32_t rhs = level == 1u ? p->err_text :
                           level == 2u ? p->category : p->category_alt;
            uint32_t len = level == 1u ? 3u : 4u;
            carry = p->compare(p->category, rhs, len);
            if (carry != 0u) continue;
        }
        if ((p->log_flags() & 2u) != 0u)
            p->log_extended(level, p->smp_text, p->source, p->file,
                            307u, p->function, id);
        return 0u;
    }
    carry = p->log_gate(carry);
    if (carry != 0u && p->compare(p->smp_text, p->hci_text, 3u) == 0u)
        return 0u;
    p->trace(p->category, p->function, id);
    return 0u;
}
