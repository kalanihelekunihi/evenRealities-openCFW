/* Four twelve-byte font-chain descriptors per ring, from Apollo Main's
 * authenticated initialized low-RAM record (stock RAM 0x20002c48 / 0x20002c78).
 * Fix 37: the +4 pointer words were raw stock RAM addresses (0x20000b54, 0x20000b78,
 * 0x20002c00, 0x20000af8 / 0x20000b9c, 0x20000bc0, 0x20002c24, 0x20000af8; init image
 * +0x2c48/+0x2c78). They now point to the objects that own those stock cells:
 * g2_ring_font_* (below) and audio_uart_font_*_active
 * (display_ring_active_data_20002c00.c). */
#include <stdint.h>
/* Fix 37: font_manager chain fonts, stock RAM 0x20000af8 and 0x20000b54..0x20000be4
 * (.data, 0x24-byte lv_font_t each). Evidence: stock init image
 * .waves/init_20000000.bin +0xaf8/+0xb54/+0xb78/+0xb9c/+0xbc0 = {0x4b26a5, 0x4b239d, 0,
 * line_height, base_line, 0x1fe00, dsc, 0, 0}. These are the entries the ring descriptors at
 * 0x20002c48/0x20002c78 point to (+4 of each 12-byte row). 0x20000b1c/0x20000b38 between
 * them are registry contexts (registry_context_data.c). Callbacks are bound by symbol, as in
 * display_ring_active_data_20002c00.c.
 * GUESS/OPEN: the dsc words are stock flash lv_font_fmt_txt_dsc_t addresses (0x77f374..)
 * whose glyph data is not ported yet (flash-address item); they stay raw. */
/* Fix 50: dsc words now point at the lv_font_fmt_txt_dsc_t objects recovered from stock bytes in
 * rom_fonts_data.c (.waves/sim-fix/fontx.py; bitmap_index delta check: 0 mismatches for all five). */
extern const unsigned char g2_ring_font_dsc_77f374[], g2_ring_font_dsc_77f414[], g2_ring_font_dsc_77f428[],
    g2_ring_font_dsc_77f464[], g2_ring_font_dsc_77f478[];
extern const void *audio_uart_lv_font_glyph_dsc_4b26a4();
extern const void *audio_uart_lv_font_glyph_bitmap_4b239c();
#define FN(f) ((uint32_t)(uintptr_t)&(f))
#define FONT(addr, lh, bl, dsc) \
    __attribute__((aligned(4), used)) uint32_t g2_ring_font_##addr[9] = { \
        FN(audio_uart_lv_font_glyph_dsc_4b26a4), FN(audio_uart_lv_font_glyph_bitmap_4b239c), \
        0u, lh, bl, 0x1fe00u, dsc, 0u, 0u}
FONT(20000af8, 0x14u, 2u, (uint32_t)(uintptr_t)&g2_ring_font_dsc_77f374);
FONT(20000b54, 0x1bu, 5u, (uint32_t)(uintptr_t)&g2_ring_font_dsc_77f414);
FONT(20000b78, 0x1au, 5u, (uint32_t)(uintptr_t)&g2_ring_font_dsc_77f428);
FONT(20000b9c, 0x1du, 6u, (uint32_t)(uintptr_t)&g2_ring_font_dsc_77f464);
FONT(20000bc0, 0x1bu, 5u, (uint32_t)(uintptr_t)&g2_ring_font_dsc_77f478);
extern uint32_t audio_uart_font_primary_active[], audio_uart_font_secondary_active[];
#define P(o) ((uint32_t)(uintptr_t)(o))

#define RING_DATA(name) \
    __attribute__((section(".data.opencfw.ring." #name), aligned(4), used)) \
    const uint32_t audio_uart_ring_##name##_descriptors[12]

RING_DATA(primary) = {
    0u, P(g2_ring_font_20000b54), 0u,
    0u, P(g2_ring_font_20000b78), 0u,
    0u, P(audio_uart_font_primary_active), 0u,
    0u, P(g2_ring_font_20000af8), 0u
};
RING_DATA(secondary) = {
    0u, P(g2_ring_font_20000b9c), 0u,
    0u, P(g2_ring_font_20000bc0), 0u,
    0u, P(audio_uart_font_secondary_active), 0u,
    0u, P(g2_ring_font_20000af8), 0u
};

_Static_assert(sizeof(audio_uart_ring_primary_descriptors) == 48, "primary ring extent");
_Static_assert(sizeof(audio_uart_ring_secondary_descriptors) == 48, "secondary ring extent");
