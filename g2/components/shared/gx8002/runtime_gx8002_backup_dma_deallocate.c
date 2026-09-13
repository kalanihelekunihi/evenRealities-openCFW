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

/* Backup 0x3d500: only the first two flags are tested, even for count > 2. */
void open_cfw_gx8002_backup_dma_deallocate(uint32_t channel)
{
    uint32_t token = open_cfw_gx8002_backup_irq_save();
    open_cfw_gx8002_backup_dma_state.allocation[channel] = 0;
    uint32_t count = open_cfw_gx8002_backup_dma_state.count;
    volatile uint8_t *allocation = open_cfw_gx8002_backup_dma_state.allocation;
    if (count != 0 && (allocation[0] == 1 || (count > 1 && allocation[1] == 1)))
        goto restore;
    open_cfw_gx8002_backup_dma_resource(25, 0);
restore:
    open_cfw_gx8002_backup_irq_restore(token);
}
