/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern volatile uint32_t open_cfw_gx8002_dma_callbacks[];
/* Stock stores private data two words after the channel's callback slot.
 * No range validation or return value is present in this leaf. */
void open_cfw_gx8002_dma_callback(uint32_t channel, uint32_t callback, uint32_t private_data)
{
    volatile uint32_t *slot=(volatile uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)open_cfw_gx8002_dma_callbacks+(channel<<2));
    slot[0]=callback;
    slot[2]=private_data;
}
