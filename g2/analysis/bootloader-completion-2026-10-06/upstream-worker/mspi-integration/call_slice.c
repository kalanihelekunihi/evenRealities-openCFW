#include <stdint.h>
extern uint32_t am_hal_mspi_disable(void *);
extern uint32_t am_hal_mspi_device_configure(void *, const void *);
extern uint32_t am_hal_mspi_enable(void *);
extern uint32_t am_hal_mspi_control(void *, uint32_t, void *);

/* Reproduce the source call sequence in bootloader 0x00420e08 and
 * 0x00420e8c. The fixed requests are XIP_CONFIG (0x10) and CLOCK_CONFIG
 * (0x18) in the pinned public header. */
uint32_t opencfw_mspi_nor_setup_slice(void *handle,
                                      const void *device_config,
                                      void *xip_config,
                                      void *clock_config)
{
    uint32_t status = am_hal_mspi_disable(handle);
    if (status != 0u) return status;
    status = am_hal_mspi_device_configure(handle, device_config);
    if (status != 0u) return status;
    status = am_hal_mspi_enable(handle);
    if (status != 0u) return status;
    (void)am_hal_mspi_control(handle, 0x10u, xip_config);
    return am_hal_mspi_control(handle, 0x18u, clock_config);
}
