/* Native image-B 0x100082a8..0x10008534, DW SPI transfer callback.
 * The pinned NationalChip spi.h establishes spi_device/spi_message/
 * spi_transfer field roles; native instructions establish the MMIO order,
 * byte/halfword/word FIFO lanes, 0/-22 results and unbounded waits.
 * Hardware FIFO timing and full message-domain equivalence remain to be
 * qualified independently of the selected C-source archive.
 */
#include <stdint.h>

extern void gx8002_image_b_platform_gate_10003be8(uint32_t, uint32_t);

static volatile uint32_t *const spi_gate =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0300080);

static uint32_t get_word(const void *record, uint32_t offset)
{
    return *(const uint32_t *)(const void *)((const uint8_t *)record + offset);
}

static void set_word(void *record, uint32_t offset, uint32_t value)
{
    *(uint32_t *)(void *)((uint8_t *)record + offset) = value;
}

static uint32_t spi_fifo_read(const uint8_t *source, uint32_t width)
{
    if (width == 1u)
        return *(const uint8_t *)(const void *)source;
    if (width == 2u)
        return *(const uint16_t *)(const void *)source;
    return *(const uint32_t *)(const void *)source;
}

static void spi_fifo_write(uint8_t *destination, uint32_t width,
                           uint32_t value)
{
    if (width == 1u)
        *(uint8_t *)(void *)destination = (uint8_t)value;
    else if (width == 2u)
        *(uint16_t *)(void *)destination = (uint16_t)value;
    else
        *(uint32_t *)(void *)destination = value;
}

int32_t gx8002_image_b_spi_callback_100082a8(void *spi,
                                                void *message)
{
    uint32_t master = get_word(spi, 0u);
    uint8_t *const device =
        (uint8_t *)(uintptr_t)get_word((void *)(uintptr_t)master, 0x18u);
    uint32_t active = get_word(device, 0x10u);
    set_word(message, 0x18u, 0u);
    set_word(message, 0x08u, (uint32_t)(uintptr_t)spi);
    if (active != 0u) {
        set_word(device, 0x10u, 0u);
        set_word(device, 0x14u, 0u);
        return 0;
    }
    set_word(device, 0x10u, (uint32_t)(uintptr_t)message);
    gx8002_image_b_platform_gate_10003be8(14u, 1u);
    spi_gate[3] = 2u;

    uint32_t node = get_word(message, 0u);
    int32_t result = 0;
    volatile uint32_t *const hardware =
        (volatile uint32_t *)(uintptr_t)get_word(device, 0x04u);
    while (node != (uint32_t)(uintptr_t)message) {
        uint8_t *const transfer = (uint8_t *)(uintptr_t)(node - 24u);
        uint32_t tx = get_word(transfer, 0u);
        uint32_t rx = get_word(transfer, 4u);
        uint32_t length = get_word(transfer, 8u);
        set_word(device, 0x14u, (uint32_t)(uintptr_t)transfer);
        uint32_t selected = tx != 0u ? tx : rx;
        set_word(device, 0x18u, selected);
        set_word(device, 0x1cu, length);

        uint32_t bits = transfer[0x0du];
        if (bits == 0u) {
            bits = 8u;
            transfer[0x0du] = 8u;
        }
        uint32_t rounded = (bits + 7u) & ~7u;
        uint32_t width = rounded == 24u ? 4u : rounded / 8u;
        device[0x28u] = (uint8_t)width;
        uint32_t message_spi = get_word(message, 0x08u);
        uint32_t config = get_word((void *)(uintptr_t)message_spi, 0x0cu);
        uint32_t control = (bits - 1u) |
            get_word((void *)(uintptr_t)config, 4u) |
            (tx != 0u ? 1024u : 2048u);
        hardware[0x08u / 4u] = 0u;
        hardware[0xf0u / 4u] = get_word((void *)(uintptr_t)config, 0x0cu);
        hardware[0] = control;
        uint32_t mode = get_word((void *)(uintptr_t)config, 0x08u);
        hardware[0x14u / 4u] = (uint16_t)mode <= 1u ? 2u : (uint16_t)mode;
        hardware[0x04u / 4u] = 0u;
        hardware[0x4cu / 4u] = 0u;
        if (length % width != 0u ||
            selected % width != 0u) {
            result = -22;
            break;
        }
        set_word(device, 0x20u, 0u);
        hardware[0x08u / 4u] = 0u;
        hardware[0x10u / 4u] = 1u;
        hardware[0x4cu / 4u] = 0u;

        uint32_t remaining = length / width;
        if (tx != 0u) {
            hardware[0x08u / 4u] = 1u;
            const uint8_t *cursor = (const uint8_t *)(uintptr_t)tx;
            while (remaining != 0u) {
                uint32_t mask = get_word(device, 0x0cu) * 2u - 1u;
                int32_t room = (int32_t)get_word(device, 0x08u) -
                    (int32_t)(mask & hardware[0x20u / 4u]);
                int32_t chunk = room < (int32_t)remaining ?
                    room : (int32_t)remaining;
                hardware[0x04u / 4u] = (uint32_t)(chunk - 1);
                for (int32_t i = 0; i < chunk; ++i) {
                    if (width == 1u || width == 2u || width == 4u) {
                        hardware[0x60u / 4u] = spi_fifo_read(cursor, width);
                        cursor += width;
                    }
                }
                remaining -= (uint32_t)chunk;
            }
        } else {
            uint8_t *cursor = (uint8_t *)(uintptr_t)rx;
            while (remaining != 0u) {
                uint32_t depth = get_word(device, 0x0cu);
                uint32_t chunk = remaining < depth ? remaining : depth;
                hardware[0x04u / 4u] = chunk - 1u;
                hardware[0x08u / 4u] = 1u;
                hardware[0x60u / 4u] = 0u;
                uint32_t left = chunk;
                while (left != 0u) {
                    int32_t available = (int32_t)
                        ((depth * 2u - 1u) & hardware[0x24u / 4u]);
                    if (available <= 0)
                        continue;
                    for (int32_t i = 0; i < available; ++i) {
                        if (width == 1u || width == 2u || width == 4u) {
                            uint32_t value = hardware[0x60u / 4u];
                            spi_fifo_write(cursor, width, value);
                            cursor += width;
                        }
                        --left;
                    }
                }
                remaining -= chunk;
            }
        }
        while ((hardware[0x28u / 4u] & 4u) == 0u) {
        }
        while ((hardware[0x28u / 4u] & 1u) != 0u) {
        }
        node = *(const uint32_t *)(uintptr_t)node;
        hardware[0x08u / 4u] = 0u;
    }

    spi_gate[3] = 3u;
    gx8002_image_b_platform_gate_10003be8(14u, 0u);
    set_word(device, 0x10u, 0u);
    set_word(device, 0x14u, 0u);
    return result;
}
