/* Selected seven-word font configuration state extents in initialized RAM.
 * Full original allocations and final image startup copy remain open. */
#include <stdint.h>

/* Sim-test fix (2026-10-26): word 0/1 of each lv_font_t are the stock Thumb
 * pointers 0x004b26a5/0x004b239d = get_glyph_dsc 0x4b26a4 / get_glyph_bitmap
 * 0x4b239c (lv_font_get_glyph_dsc_fmt_txt / lv_font_get_bitmap_fmt_txt, the
 * same pair rom_fonts_data.c binds by symbol). As literal stock addresses
 * they pointed into unrelated code in our layout. Now symbol references;
 * storage stays uint32_t[7] (32-bit pointers on this target). */
extern const void *audio_uart_lv_font_glyph_dsc_4b26a4();
extern const void *audio_uart_lv_font_glyph_bitmap_4b239c();
#define FN(f) ((uint32_t)(uintptr_t)&(f))

#define FONT_ACTIVE(name) \
    __attribute__((section(".data.opencfw.font." #name "_active"), aligned(4), used)) \
    uint32_t audio_uart_font_##name##_active[7]

FONT_ACTIVE(primary) = {FN(audio_uart_lv_font_glyph_dsc_4b26a4), FN(audio_uart_lv_font_glyph_bitmap_4b239c), 0u, 0x1au,
                        0x6u, 0x1fd00u, 0u};
FONT_ACTIVE(secondary) = {FN(audio_uart_lv_font_glyph_dsc_4b26a4), FN(audio_uart_lv_font_glyph_bitmap_4b239c), 0u, 0x1cu,
                          0x6u, 0x1fd00u, 0u};

_Static_assert(sizeof(audio_uart_font_primary_active) == 28, "primary selected extent");
_Static_assert(sizeof(audio_uart_font_secondary_active) == 28, "secondary selected extent");
