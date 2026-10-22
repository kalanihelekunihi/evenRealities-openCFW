/* Stock D:\01_workspace\s200_ap510b_iar_git\third_party\lvgl_v9.3\LVGL\src\font\lv_font.c
 * (product-modified LVGL 9.3 lv_font.c), two functions of that unit:
 *   0x4d5590..0x4d559b  lv_memzero, the lv_string.h `static inline` copy IAR
 *                       emitted in this unit (body identical to upstream)
 *   0x4d5664..0x4d56bf  lv_font_glyph_release_draw_data, product variant;
 *                       literal pool 0x4d5858..0x4d5877
 *
 * Difference from upstream (third-party/upstream/lvgl/src/font/lv_font.c):
 * when the font descriptor (lv_font_t.dsc, +0x18) lies in the memory-mapped
 * NOR flash window (address >= 0x80000001), the release_glyph callback runs
 * with the MX25U NOR flash lock held (0x46f65e / 0x46f674), as does the
 * product lv_font_get_glyph_bitmap at 0x4d5612. The assertion is reported
 * from source line 67 (upstream line 58). */
#include <stdint.h>
#include <stddef.h>

#define NOR_XIP_FONT_DSC_MIN 0x80000001u

typedef struct g2_lv_font g2_lv_font_t;
typedef struct g2_lv_font_glyph_dsc g2_lv_font_glyph_dsc_t;

/* lv_font_t, LVGL 9.3 layout. */
struct g2_lv_font {
    void *get_glyph_dsc;                                              /* +0x00 */
    void *get_glyph_bitmap;                                           /* +0x04 */
    void (*release_glyph)(const g2_lv_font_t *, g2_lv_font_glyph_dsc_t *); /* +0x08 */
    int32_t line_height;                                              /* +0x0c */
    int32_t base_line;                                                /* +0x10 */
    uint8_t subpx_kerning;                                            /* +0x14 bitfield */
    int8_t underline_position;                                        /* +0x15 */
    int8_t underline_thickness;                                       /* +0x16 */
    const void *dsc;                                                  /* +0x18 */
    const g2_lv_font_t *fallback;                                     /* +0x1c */
    void *user_data;                                                  /* +0x20 */
};
_Static_assert(offsetof(struct g2_lv_font, dsc) == 0x18u, "lv_font_t.dsc");

/* lv_font_glyph_dsc_t, only the fields used here. */
struct g2_lv_font_glyph_dsc {
    const g2_lv_font_t *resolved_font; /* +0x00 */
    uint8_t opaque_04[0x18];           /* +0x04 adv_w, box, ofs, format, gid */
    void *entry;                       /* +0x1c lv_cache_entry_t * */
};
_Static_assert(offsetof(struct g2_lv_font_glyph_dsc, entry) == 0x1cu, "lv_font_glyph_dsc_t.entry");

/* lv_memset(dst, value, len), stock 0x454746 (name from existing g2/src units). */
extern void audio_uart_lv_basic_box_clear_454746(void *dst, uint32_t value, uint32_t len);
extern void audio_uart_lvgl_log(uint32_t level, const char *file, uint32_t line,
                                const char *function, const char *format, ...); /* lv_log_add 0x44d25c */
extern void g2_norflash_lock_46f65e(void);
extern void g2_norflash_unlock_46f674(void);

static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\font\\lv_font.c"; /* ROM 0x6e8698 */
static const char function[] = "lv_font_glyph_release_draw_data"; /* ROM 0x760e90 */
static const char assertion[] = "Asserted at expression: %s (%s)"; /* ROM 0x760e70 */
static const char expression[] = "g_dsc != NULL";                  /* ROM 0x786920 */
static const char reason[] = "NULL pointer";                       /* ROM 0x786910 */


void lv_font_glyph_release_draw_data_4d5664(g2_lv_font_glyph_dsc_t *g_dsc)
{
    const g2_lv_font_t *font;

    if (g_dsc == NULL) {
        audio_uart_lvgl_log(3u, source, 0x43u, function, assertion, expression, reason);
        for (;;)
            *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u; /* LV_ASSERT_HANDLER */
    }
    if (g_dsc->entry == NULL)
        return;
    font = g_dsc->resolved_font;
    if (font == NULL || font->release_glyph == NULL)
        return;
    if ((uintptr_t)font->dsc >= NOR_XIP_FONT_DSC_MIN)
        g2_norflash_lock_46f65e();
    font->release_glyph(font, g_dsc);
    if ((uintptr_t)font->dsc >= NOR_XIP_FONT_DSC_MIN)
        g2_norflash_unlock_46f674();
}
