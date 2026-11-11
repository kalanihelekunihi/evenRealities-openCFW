/* SPDX-License-Identifier: MIT
 * BINH A stage-1 NOR read path at stock 0x10000c40..0x10000e44.
 * The register writes, JEDEC cases, XIP setup and 64 KiB chunk loop follow
 * the locked C-SKY disassembly. This is a source candidate, not a proven
 * byte match or a hardware-qualified SPI implementation.
 */
#include <stdint.h>

extern void gx8002_image_a_stage1_clock_gate_100005a4(
    uint32_t module, uint32_t enabled);
extern uint32_t gx8002_image_a_stage1_flash_transaction_10000bbc(
    uint32_t command, uint8_t *destination, uint32_t bytes);
extern uint32_t gx8002_image_a_stage1_flash_write_10000b5c(
    uint32_t command, const uint8_t *source, uint32_t bytes);
extern uint32_t gx8002_image_a_stage1_udiv_10000af8(
    uint32_t numerator, uint32_t denominator);

static volatile uint32_t *const spi =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000000);
static volatile uint32_t *const spi_aux =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000080);
static volatile uint32_t *const xip =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000100);
static volatile uint32_t *const flash_id =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x20001290);

/* Stock 0x10000b4c..0x10000b5c polls SPIM_SR bit 0 until idle. */
__attribute__((used, section(".spl_a.wait_bus")))
uint32_t gx8002_image_a_stage1_wait_bus_10000b4c(void)
{
    while ((spi[0x28u / 4u] & 1u) != 0u) {}
    return 0u;
}

/* Stock 0x10000c1c returns one after status bit 0 clears. */
__attribute__((used, section(".spl_a.wait_ready")))
uint32_t gx8002_image_a_stage1_wait_ready_10000c1c(void)
{
    uint8_t status;
    do {
        (void)gx8002_image_a_stage1_flash_transaction_10000bbc(
            5u, &status, 1u);
    } while ((status & 1u) != 0u);
    return 1u;
}

static void initialize_flash_and_xip(void)
{
    volatile uint32_t *const auxiliary =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0300080);
    uint8_t id_bytes[3];
    uint8_t second_status;
    auxiliary[0x10u / 4u] = 1u;
    spi[0x08u / 4u] = 0u;
    spi[0x2cu / 4u] = 0u;
    spi_aux[0x70u / 4u] = 1u;
    spi[0x14u / 4u] = 2u;
    spi[0x1cu / 4u] = 31u;
    spi[0x08u / 4u] = 1u;
    if (gx8002_image_a_stage1_flash_transaction_10000bbc(
            159u, id_bytes, 3u) != 0u)
        return;

    uint32_t id = ((uint32_t)id_bytes[0] << 16) |
                  ((uint32_t)id_bytes[1] << 8) | id_bytes[2];
    *flash_id = id;
    /* ESMT EN25S20A/EN25S40A need no quad-enable write. The PUYA parts
     * use a combined status-1/status-2 write; other parts write status 2. */
    if (id == UINT32_C(0x1c3812) || id == UINT32_C(0x1c3813)) {
        /* Keep the existing status bytes and proceed to XIP setup. */
    } else if (id == UINT32_C(0x854012) ||
               id - UINT32_C(0x856013) < 2u) {
        (void)gx8002_image_a_stage1_flash_transaction_10000bbc(
            5u, &id_bytes[0], 1u);
        (void)gx8002_image_a_stage1_flash_transaction_10000bbc(
            53u, &second_status, 1u);
        id_bytes[1] = second_status;
        if ((second_status & 2u) == 0u) {
            id_bytes[1] = (uint8_t)(second_status | 2u);
            (void)gx8002_image_a_stage1_wait_ready_10000c1c();
            (void)gx8002_image_a_stage1_flash_write_10000b5c(6u, 0, 0u);
            (void)gx8002_image_a_stage1_flash_write_10000b5c(
                1u, id_bytes, 2u);
            (void)gx8002_image_a_stage1_wait_ready_10000c1c();
        }
    } else {
        (void)gx8002_image_a_stage1_flash_transaction_10000bbc(
            53u, &second_status, 1u);
        if ((second_status & 2u) == 0u) {
            second_status = (uint8_t)(second_status | 2u);
            (void)gx8002_image_a_stage1_wait_ready_10000c1c();
            (void)gx8002_image_a_stage1_flash_write_10000b5c(6u, 0, 0u);
            (void)gx8002_image_a_stage1_flash_write_10000b5c(
                49u, &second_status, 1u);
            (void)gx8002_image_a_stage1_wait_ready_10000c1c();
        }
    }

    /* Stock 0x10000d4a..0x10000d8a configures the XIP controller and
     * leaves the flash clock enabled for execution in place. */
    spi[0x08u / 4u] = 0u;
    xip[0x14u / 4u] = 255u;
    xip[0x08u / 4u] = UINT32_C(0x08c09406) |
                       (gx8002_image_a_stage1_udiv_10000af8(24u, 4u) << 4);
    xip[0x0cu / 4u] = 1u;
    xip[0x00u / 4u] = 235u;
    xip[0x04u / 4u] = 235u;
    auxiliary[0x10u / 4u] = 0u;
    spi[0x08u / 4u] = 1u;
}

static void read_chunk(uint32_t source_offset, uint8_t *destination,
                       uint32_t bytes)
{
    gx8002_image_a_stage1_wait_bus_10000b4c();
    spi[0x4cu / 4u] = 0u;
    spi[0x08u / 4u] = 0u;
    spi[0x10u / 4u] = 0u;
    spi[0x00u / 4u] = UINT32_C(0x00800807);
    spi[0x04u / 4u] = bytes - 1u;
    spi[0x18u / 4u] = 0u;
    spi[0x54u / 4u] = 7u;
    if ((*flash_id + UINT32_C(0xffe3c7ee)) < 2u) {
        spi_aux[0x74u / 4u] = UINT32_C(0x40003219);
        spi[0x08u / 4u] = 1u;
        spi[0x64u / 4u] = 235u;
    } else {
        spi_aux[0x74u / 4u] = UINT32_C(0x40004218);
        spi[0x08u / 4u] = 1u;
        spi[0x64u / 4u] = 107u;
    }
    spi[0x64u / 4u] = source_offset;
    spi[0x10u / 4u] = 1u;
    for (uint32_t i = 0u; i < bytes; ++i) {
        while ((spi[0x28u / 4u] & 8u) == 0u) {}
        destination[i] = (uint8_t)spi[0x60u / 4u];
    }
    while (spi[0x24u / 4u] != 0u) {}
    gx8002_image_a_stage1_wait_bus_10000b4c();
}

__attribute__((used, section(".spl_a.text")))
uint32_t gx8002_image_a_stage1_flash_read_10000c40(
    uint32_t source_offset, void *destination, uint32_t bytes)
{
    uint8_t *cursor = destination;
    gx8002_image_a_stage1_clock_gate_100005a4(13u, 1u);
    if (*flash_id == UINT32_C(0x00ffffff))
        initialize_flash_and_xip();
    (void)gx8002_image_a_stage1_wait_ready_10000c1c();
    while (bytes != 0u) {
        uint32_t take = bytes < UINT32_C(0x10000)
            ? bytes : UINT32_C(0x10000);
        read_chunk(source_offset, cursor, take);
        source_offset += take;
        cursor += take;
        bytes -= take;
    }
    return 0u;
}
