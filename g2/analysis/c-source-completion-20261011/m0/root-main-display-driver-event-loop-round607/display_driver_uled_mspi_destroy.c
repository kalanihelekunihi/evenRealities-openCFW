/* Apollo 0x4c240e, candidate translation from original Thumb instructions.
 * The six direct callees remain imports until independently reconstructed.
 */
#include <stdint.h>
#include <stddef.h>

#define ULED_MSPI_MAGIC 0x01bebebeu
#define ULED_MSPI_BASE 0x40060000u

extern uint32_t display_driver_uled_mspi_queue_snapshot_53901a(uint32_t, uint32_t *);
extern uint32_t display_driver_uled_mspi_queue_release_5390fc(uint32_t);
extern uint32_t display_driver_uled_mspi_dma_start_4bfd44(uint32_t *);
extern uint32_t display_driver_uled_mspi_dma_stop_4bfd62(uint32_t *);
extern uint32_t display_driver_uled_mspi_dma_next_4bfdf4(uint32_t *);
extern uint32_t display_driver_uled_mspi_pin_control_4c4530(uint32_t, uint32_t);

static uint32_t word(const uint32_t *h, uint32_t off) { return h[off / 4u]; }
static void put_word(uint32_t *h, uint32_t off, uint32_t v) { h[off / 4u] = v; }
static uint8_t byte(const uint32_t *h, uint32_t off) { return ((const uint8_t *)h)[off]; }
static void put_byte(uint32_t *h, uint32_t off, uint8_t v) { ((uint8_t *)h)[off] = v; }
static volatile uint32_t *regs(uint32_t instance) {
    return (volatile uint32_t *)(uintptr_t)(ULED_MSPI_BASE + (instance << 12));
}
typedef void (*uled_completion)(uint32_t, uint32_t);
static void complete(uint32_t *h, uint32_t index, uint32_t status) {
    uint32_t callback = h[10u + index];
    if (callback != 0u) {
        ((uled_completion)(uintptr_t)callback)(h[0x10au + index], status);
        if (byte(h, 0x82cu) != 2u) h[10u + index] = 0u;
    }
}
static void stop_mspi(volatile uint32_t *r) {
    r[0x100u / 4u] &= ~3u;
    r[0x30u / 4u] &= ~0x40000000u;
    r[0x30u / 4u] |= 0x40000000u;
}

uint32_t display_driver_uled_mspi_child_4c240e(uint32_t *h,
                                                  uint32_t flags,
                                                  uint32_t arg2,
                                                  uint32_t arg3) {
    if (h == NULL || (h[0] & 0x01ffffffu) != ULED_MSPI_MAGIC) return 2u;
    uint32_t instance = h[1];
    volatile uint32_t *r = regs(instance);
    uint32_t status;
    if (byte(h, 0x83cu) != 0u) {
        put_word(h, 0x24u, word(h, 0x24u) | flags);
        if ((word(h, 0x24u) & 0x18c0u) == 0u) return 0u;
        while ((r[0x104u / 4u] & 1u) != 0u) { }
        put_word(h, 0x24u, word(h, 0x24u) | r[0x204u / 4u]);
        r[0x208u / 4u] = 0xffffffffu;
        uint32_t fatal = (word(h, 0x24u) & 0x1880u) != 0u;
        if (fatal) stop_mspi(r);
        put_word(h, 0x850u, word(h, 0x850u) + 1u);
        put_word(h, 0x840u, word(h, 0x840u) - 1u);
        uint32_t ring_index = word(h, 0x850u) % word(h, 0x848u);
        uint32_t *entry = (uint32_t *)(uintptr_t)(word(h, 0x854u) + ring_index * 0x18u);
        if (entry[4] != 0u) {
            ((uled_completion)(uintptr_t)entry[4])(entry[5], fatal);
            entry[4] = 0u;
        }
        if (word(h, 0x840u) != 0u) {
            put_word(h, 0x24u, 0u);
            (void)display_driver_uled_mspi_dma_next_4bfdf4(h);
            return 0u;
        }
        put_byte(h, 0x83cu, 0u);
        r[0x100u / 4u] = 0u;
        r[0x200u / 4u] &= ~0x40u;
        r[0x2b4u / 4u] = 0x80u;
        if (word(h, 0x20u) == 0u && byte(h, 0x8c9u) != 4u) {
            status = display_driver_uled_mspi_pin_control_4c4530(4u, (instance + 0x10u) & 0xffu);
            if (status != 0u) return status;
        }
        return 0u;
    }
    if (word(h, 0x20u) == 0u) return 0u;
    put_word(h, 0x24u, word(h, 0x24u) | flags);
    uint32_t queue_handle = *(volatile uint32_t *)(uintptr_t)(0x20052c00u + instance * 0x8d0u);
    if (queue_handle != 0u) {
        uint32_t snapshot[4] = {(uint32_t)(uintptr_t)h, flags, arg2, arg3};
        status = display_driver_uled_mspi_queue_snapshot_53901a(queue_handle, snapshot);
        if (status == 0u) {
            put_byte(h, 0x834u, 0u);
            while (byte(h, 0x834u) == 0u && word(h, 0x1cu) != snapshot[0]) {
                put_word(h, 0x1cu, word(h, 0x1cu) + 1u);
                put_word(h, 0x20u, word(h, 0x20u) - 1u);
                complete(h, byte(h, 0x1cu), 0u);
            }
            if (byte(h, 0x834u) == 0u) {
                if ((flags & 0x1880u) != 0u || ((snapshot[3] >> 16) & 0xffu) != 0u) {
                    put_word(h, 0x1cu, word(h, 0x1cu) + 1u);
                    put_word(h, 0x20u, word(h, 0x20u) - 1u);
                    complete(h, byte(h, 0x1cu), 1u);
                    status = display_driver_uled_mspi_dma_stop_4bfd62(h);
                    if (status != 0u) return status;
                    stop_mspi(r);
                    r[0x2acu / 4u] = r[0x2acu / 4u];
                    (void)display_driver_uled_mspi_queue_release_5390fc(queue_handle);
                    if (word(h, 0x20u) != 0u) {
                        status = display_driver_uled_mspi_dma_start_4bfd44(h);
                        if (status != 0u) return status;
                    }
                }
                if (word(h, 0x20u) == 0u) {
                    status = display_driver_uled_mspi_dma_stop_4bfd62(h);
                    if (status != 0u) return status;
                }
            }
        }
    }
    if (word(h, 0x20u) == 0u) {
        r[0x100u / 4u] &= ~3u;
        if (byte(h, 0x8c9u) != 4u) {
            status = display_driver_uled_mspi_pin_control_4c4530(4u, (instance + 0x10u) & 0xffu);
            if (status != 0u) return status;
        }
    }
    return 0u;
}
