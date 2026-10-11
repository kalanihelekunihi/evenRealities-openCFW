/* SPDX-License-Identifier: MIT
 * Native XIP 0x102055f4, 0x10205860/98, 0x102059e8.
 * These are actual register/cache provider bodies for the SNPU submit
 * branch; 0x10025664 cache cleaner is selected resident source.
 */
#include <stdint.h>

extern void gx8002_xip_register_set_bit_102055cc(uint32_t, uint32_t);
extern uint32_t gx8002_xip_register_read_102055ec(uint32_t);
extern void gx8002_xip_register_write_102055f0(uint32_t, uint32_t);
extern void g2_codec_header_sync(void *, uint32_t);

void gx8002_xip_npu_enable_102055f4(uint32_t base)
{
    gx8002_xip_register_set_bit_102055cc(base, 0u);
}

void gx8002_xip_npu_get_over_command_10205860(
    uint32_t base, uint32_t *out_address)
{
    *out_address = gx8002_xip_register_read_102055ec(base + 0x104u);
}

void gx8002_xip_npu_set_task_head_10205898(uint32_t base, uint32_t address)
{
    gx8002_xip_register_write_102055f0(base + 0x10u, address);
}

void gx8002_xip_snpu_task_cache_flush_102059e8(uint32_t *task)
{
    g2_codec_header_sync(task, 8u);
    g2_codec_header_sync((uint8_t *)task + 16u, 0x6cu);
}
