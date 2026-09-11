/* SPDX-License-Identifier: MIT */
#include "runtime_gx8002_dma_layout.h"
/* Source-owned analysis storage. Startup must zero BSS before use.
 * Word arrays match the existing consumer declarations. Descriptor alignment
 * is performed by dma_initialize inside the reserved per-channel storage. */
volatile uint32_t open_cfw_gx8002_dma_state[
    sizeof(struct open_cfw_gx8002_dma_layout) / sizeof(uint32_t)];
volatile uint32_t open_cfw_gx8002_dma_callbacks[4];
_Static_assert(sizeof(open_cfw_gx8002_dma_state)==884,"DMA storage extent");
_Static_assert(sizeof(open_cfw_gx8002_dma_callbacks)==16,"DMA callback extent");
