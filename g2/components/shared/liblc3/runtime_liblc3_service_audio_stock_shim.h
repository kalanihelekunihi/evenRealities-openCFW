/*
 * SPDX-License-Identifier: MIT
 *
 * Exact stock service_audio LC3 ABI bridge for the bounded adapter.
 */
#ifndef OPEN_CFW_RUNTIME_LIBLC3_SERVICE_AUDIO_STOCK_SHIM_H
#define OPEN_CFW_RUNTIME_LIBLC3_SERVICE_AUDIO_STOCK_SHIM_H

#include <stdint.h>

#define OPEN_CFW_LIBLC3_STOCK_CONTEXT_0 UINT32_C(0x20106A7C)
#define OPEN_CFW_LIBLC3_STOCK_CONTEXT_1 UINT32_C(0x201074C0)
#define OPEN_CFW_LIBLC3_STOCK_CONTEXT_2 UINT32_C(0x20107F04)
#define OPEN_CFW_LIBLC3_STOCK_CONTEXT_3 UINT32_C(0x20108948)
#define OPEN_CFW_LIBLC3_STOCK_CONTEXT_END UINT32_C(0x2010938C)

/* Stock entry at 0x0057A926: lazy setup has no status result. */
void open_cfw_liblc3_service_audio_stock_setup(void *stock_context);

/* Stock entry at 0x0057A940: zero succeeds and -1 fails. */
int32_t open_cfw_liblc3_service_audio_stock_encode(
    const void *pcm,
    uint32_t pcm_bytes,
    void *output,
    int32_t *output_bytes,
    void *stock_context);

#endif
