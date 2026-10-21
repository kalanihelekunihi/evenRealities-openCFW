/* Native image-B 0x100085ac..0x100086ac: SPI master device setup.
 * The descriptor and controller state use source-owned RAM/MMIO
 * contracts. The three callback entries are native function relocations;
 * their bodies are separate genuine source obligations.
 */
#include <stdint.h>

extern volatile uint32_t gx8002_image_b_spi_device_state_20017670[24];
extern void gx8002_image_b_platform_gate_10003be8(uint32_t, uint32_t);
extern int32_t gx8002_image_b_spi_register_master_10008218(uint32_t *);
extern void gx8002_image_b_request_irq_10004844(
    uint32_t, int32_t (*)(int32_t, void *), uint32_t);
extern uint32_t gx8002_image_b_spi_master_irq_10008288(uint32_t, void *);
extern uint32_t gx8002_image_b_spi_callback_1000827c(void);
extern uint32_t gx8002_image_b_spi_callback_10008538(void);
extern uint32_t gx8002_image_b_spi_callback_100082a8(void);

static uint32_t gx8002_image_b_spi_probe_one(
    volatile uint32_t *hardware, uint32_t command_offset,
    uint32_t status_offset)
{
    uint32_t probe = 2u;
    uint32_t remaining = 256u;
    do {
        hardware[command_offset / 4u] = probe;
        uint32_t observed = hardware[status_offset / 4u];
        if (observed != probe)
            break;
        ++probe;
    } while (--remaining != 0u);
    hardware[command_offset / 4u] = 0u;
    return remaining == 0u ? 258u : probe;
}

void gx8002_image_b_board_devices_initialize_100085ac(void)
{
    volatile uint32_t *const base = gx8002_image_b_spi_device_state_20017670;
    volatile uint32_t *const device = base + 13u;
    volatile uint32_t *const master = base + 4u;
    volatile uint32_t *const hardware =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa3000000);

    device[1] = UINT32_C(0xa3000000);
    base[0x34u / 4u] = (uint32_t)(uintptr_t)master;
    base[0x28u / 4u] = (uint32_t)(uintptr_t)device;
    base[0x10u / 4u] = 0u;
    base[0x14u / 4u] = 1u;
    master[0x10u / 4u] =
        (uint32_t)(uintptr_t)gx8002_image_b_spi_callback_1000827c;
    master[0x08u / 4u] =
        (uint32_t)(uintptr_t)gx8002_image_b_spi_callback_10008538;
    master[0x0cu / 4u] =
        (uint32_t)(uintptr_t)gx8002_image_b_spi_callback_100082a8;

    gx8002_image_b_platform_gate_10003be8(14u, 1u);
    hardware[0x08u / 4u] = 0u;
    hardware[0x2cu / 4u] = 78u;
    if (device[2] == 0u)
        device[2] = gx8002_image_b_spi_probe_one(hardware, 0x18u, 0x18u);
    if (device[3] == 0u)
        device[3] = gx8002_image_b_spi_probe_one(hardware, 0x1cu, 0x1cu);

    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa030008c) = 3u;
    hardware[0x08u / 4u] = 1u;
    if ((hardware[0x28u / 4u] & 8u) != 0u) {
        do {
            (void)hardware[0x60u / 4u];
        } while ((hardware[0x28u / 4u] & 8u) != 0u);
    }
    while ((hardware[0x28u / 4u] & 1u) != 0u) {
    }
    gx8002_image_b_platform_gate_10003be8(14u, 0u);
    device[4] = 0u;
    device[5] = 0u;
    (void)gx8002_image_b_spi_register_master_10008218(
        (uint32_t *)(void *)master);
    gx8002_image_b_request_irq_10004844(
        16u, (int32_t (*)(int32_t, void *))(uintptr_t)
                 gx8002_image_b_spi_master_irq_10008288,
        (uint32_t)(uintptr_t)device);
}
