/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern volatile uint32_t open_cfw_gx8002_backup_dma_callbacks[];
/* Original literal-pool slot retained symbolically for layout compatibility. */
__attribute__((section(".backup_callback_pointer"), used))
volatile uint32_t * const open_cfw_gx8002_backup_dma_callback_pointer =
    open_cfw_gx8002_backup_dma_callbacks;
