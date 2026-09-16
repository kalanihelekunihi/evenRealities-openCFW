/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <stddef.h>
/* Only offsets consumed by this routine are modeled here. */
struct dma_state {
    uint32_t base, count;
    uint8_t unmodeled_fields[0x368];
    uint8_t allocation[];
};
_Static_assert(offsetof(struct dma_state, count) == 4, "DMA count offset");
_Static_assert(offsetof(struct dma_state, allocation) == 0x370, "DMA allocation offset");
extern volatile struct dma_state open_cfw_gx8002_backup_dma_state;
extern uint32_t open_cfw_gx8002_backup_irq_save(void);
extern void open_cfw_gx8002_backup_irq_restore(uint32_t);
extern void open_cfw_gx8002_backup_dma_resource(uint32_t, uint32_t);

/* CK804 ld.b zero-extends its byte result. Express that result width to
 * GCC: its volatile uint8_t lowering otherwise adds a redundant zextb.
 * The memory input describes precisely the accessed allocation byte. */
static inline __attribute__((always_inline)) uint32_t read_allocation(unsigned index)
{
    uint32_t value;
    __asm__ volatile ("ld.b %0, (%1, %2)"
        : "=r" (value)
        : "r" (&open_cfw_gx8002_backup_dma_state), "i" (0x370 + index),
          "m" (open_cfw_gx8002_backup_dma_state.allocation[index]));
    return value;
}

/* Backup 0x3d500: only the first two flags are tested, even for count > 2. */
void open_cfw_gx8002_backup_dma_deallocate(uint32_t channel)
{
    uint32_t token = open_cfw_gx8002_backup_irq_save();
    open_cfw_gx8002_backup_dma_state.allocation[channel] = 0;
    uint32_t count = open_cfw_gx8002_backup_dma_state.count;
    if (count != 0 && (read_allocation(0) == 1 || (count > 1 && read_allocation(1) == 1)))
        goto restore;
    open_cfw_gx8002_backup_dma_resource(25, 0);
restore:
    open_cfw_gx8002_backup_irq_restore(token);
}
