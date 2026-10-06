/* Readable reconstruction of the locked 44-byte mspi_cq_init wrapper at
 * 0x00423f28. The lower-level am_hal_cmdq_init provider remains external. */
#include <stdint.h>
#include <stddef.h>

enum {
    MSPI_STATE_BASE = 0x2001caa0,
    MSPI_STATE_STRIDE = 0x8d0,
    MSPI_CMDQ_HANDLE_OFFSET = 0x828
};

struct mspi_cq_init_cfg_bytes {
    uint32_t queue_size_half_units;
    uint32_t queue_buffer_address;
    uint8_t queue_option;
};

extern uint32_t am_hal_cmdq_init(uint8_t hw_interface,
                                 struct mspi_cq_init_cfg_bytes *config,
                                 void **handle_slot);

_Static_assert(sizeof(struct mspi_cq_init_cfg_bytes) == 12u,
               "stock stack config first three fields require 12-byte object extent");
_Static_assert(offsetof(struct mspi_cq_init_cfg_bytes,
                        queue_size_half_units) == 0u, "stock config word0");
_Static_assert(offsetof(struct mspi_cq_init_cfg_bytes,
                        queue_buffer_address) == 4u, "stock config word1");
_Static_assert(offsetof(struct mspi_cq_init_cfg_bytes,
                        queue_option) == 8u, "stock config byte2");
_Static_assert(sizeof(uintptr_t) == 4u, "stock output slot uses ARM32 pointers");

void opencfw_bl_mspi_cq_init(uint32_t module, uint32_t queue_size_input,
                             uint32_t queue_buffer_address)
{
    struct mspi_cq_init_cfg_bytes config;
    const uint32_t slot_address = MSPI_STATE_BASE +
        module * MSPI_STATE_STRIDE + MSPI_CMDQ_HANDLE_OFFSET;

    config.queue_size_half_units = queue_size_input >> 1;
    config.queue_buffer_address = queue_buffer_address;
    config.queue_option = 1u;

    (void)am_hal_cmdq_init((uint8_t)(module + 8u), &config,
                           (void **)(uintptr_t)slot_address);
}
