/* Apollo MSPI status children 0x4c2392 and 0x4c23de. Candidate. */
#include <stdint.h>
#define MSPI_HANDLE_MAGIC 0x01bebebeu
#define MSPI_MMIO_BASE 0x40060000u
static int valid_handle(const uint32_t *handle) {
    return handle!=0 && (handle[0]&0x01ffffffu)==MSPI_HANDLE_MAGIC;
}
static volatile uint32_t *mspi_registers(const uint32_t *handle) {
    return (volatile uint32_t *)(uintptr_t)(MSPI_MMIO_BASE+(handle[1]<<12));
}
uint32_t display_driver_uled_mspi_child_4c2392(const uint32_t *handle,
                                               uint32_t *out,uint32_t both) {
    if(!valid_handle(handle))return 2u;
    volatile uint32_t *regs=mspi_registers(handle);
    uint32_t value=regs[0x204u/4u];
    if((uint8_t)both!=0u)value&=regs[0x200u/4u];
    *out=value;
    return 0u;
}
uint32_t display_driver_uled_mspi_child_4c23de(const uint32_t *handle,
                                               uint32_t mask) {
    if(!valid_handle(handle))return 2u;
    volatile uint32_t *regs=mspi_registers(handle);
    regs[0x208u/4u]=mask;
    (void)regs[0x204u/4u];
    return 0u;
}
