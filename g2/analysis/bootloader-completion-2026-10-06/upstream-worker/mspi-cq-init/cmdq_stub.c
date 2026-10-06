/* Link-only seam. The verifier intercepts this call, records the exact
 * forwarded fields/address, and leaves actual queue initialization external. */
#include <stdint.h>
struct mspi_cq_init_cfg_bytes;
uint32_t am_hal_cmdq_init(uint8_t hw_interface,
                          struct mspi_cq_init_cfg_bytes *config,
                          void **handle_slot)
{
    (void)hw_interface;
    (void)config;
    (void)handle_slot;
    return 0u;
}
