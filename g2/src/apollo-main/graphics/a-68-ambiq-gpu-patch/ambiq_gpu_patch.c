/* Ambiq LVGL NemaGFX port helpers that render 1-pixel-high pattern textures.
 * Not in the pinned third-party/upstream/ambiq-lvgl tree, which only calls them
 * (src/draw/ambiq/lv_draw_ambiq_fill.c / _triangle.c: lv_ambiq_gradient_create(
 * stops_count, stops, colors, NEMA_TEX1); lv_draw_ambiq_line.c:
 * lv_ambiq_dashline_create(dash_width, dash_gap, bg_color, NEMA_TEX1)).
 * Stock callers: 0x53dc38 and 0x53e728 (gradient), 0x53ecfc (dash line).
 *
 * lv_ambiq_gradient_create  native 0x5fa238..0x5fa7bf, literal pool 0x5fa4a0..0x5fa4bf
 *                           (mid-function), white const ROM 0x789f70.
 * lv_ambiq_dashline_create  native 0x5fa7c0..0x5fa849, literal pool 0x5fa84c.
 *
 * Callees are NemaGFX API entry points (named here by their existing g2/src
 * names): 0x4b1516 nema_set_clip, 0x513924 nema_set_blend, 0x4b1588
 * nema_enable_gradient, 0x4b199c nema_set_gradient, 0x4b1ab0 nema_fill_rect,
 * 0x4b15a6 nema_rgba, 0x522a16 nema_set_raster_color, 0x522ae0
 * nema_raster_rect, 0x4b1548 clip restore, 0x5f9f14 nema_interpolate_rect_colors
 * (NemaGFX library code, license-blocked, declared only).
 *
 * Floating point: build with profile g2-apollo-main-3. */
#include <stdint.h>
#include <stddef.h>

/* NemaGFX color_var_t. */
typedef struct {
    float r; /* +0x00 */
    float g; /* +0x04 */
    float b; /* +0x08 */
    float a; /* +0x0c */
} g2_color_var_t;
_Static_assert(sizeof(g2_color_var_t) == 0x10u, "color_var_t");

/* nema_context texture slots: stride 0x18, width at +0x3c from the context base. */
#define NEMA_CTX_TEX_WIDTH_OFFSET 0x3cu
#define NEMA_CTX_TEX_STRIDE 0x18u
#define NEMA_BL_SRC 1u
#define NEMA_NOTEX 0xffffffffu
#define GRADIENT_TEXTURE_LAST_X 63u    /* end pixel of the 64-texel gradient texture */
#define GRADIENT_STOP_FLOOR (-65535.0f) /* pool 0x5fa4bc: 0xc77fff00 */

extern volatile uint32_t audio_uart_nema_context_cell[]; /* RAM 0x20074efc: nema_context pointer */

extern void audio_uart_display_graphics_target_4b1516(int32_t x, int32_t y, uint32_t width,
                                                      uint32_t height); /* nema_set_clip */
extern void display_driver_nema_mode_513924(uint32_t blend, uint32_t dst, uint32_t fg,
                                            uint32_t bg); /* nema_set_blend */
extern void display_driver_nema_cache_4b1588(uint32_t enabled); /* nema_enable_gradient */
extern void display_driver_nema_select_522a16(uint32_t color);  /* nema_set_raster_color */
extern uint32_t audio_uart_nema_mask_rectangle_522ae0(int32_t x, int32_t y, int32_t width,
                                                      int32_t height); /* nema_raster_rect */
extern void audio_uart_ambiq_label_fill_rectangle_4b1ab0(uint32_t x, uint32_t y, uint32_t width,
                                                         uint32_t height,
                                                         uint32_t color); /* nema_fill_rect */
/* nema_rgba: first argument is the low byte (R), last the high byte (A). */
extern uint32_t audio_uart_ambiq_color_pack_4b15a6(uint32_t r, uint32_t g, uint32_t b,
                                                   uint32_t a);
extern void audio_uart_display_graphics_finish_4b1548(void); /* clip restore */
extern void nema_set_gradient_4b199c(float r_init, float g_init, float b_init, float a_init,
                                     float dr_dx, float dr_dy, float dg_dx, float dg_dy,
                                     float db_dx, float db_dy, float da_dx, float da_dy)
    __attribute__((pcs("aapcs-vfp")));
extern void nema_interpolate_rect_colors_5f9f14(int32_t x0, int32_t y0, int32_t w, int32_t h,
                                                const g2_color_var_t *col0,
                                                const g2_color_var_t *col1,
                                                const g2_color_var_t *col2);

static uint32_t nema_texture_width(uint32_t tex)
{
    const volatile uint8_t *context =
        (const volatile uint8_t *)(uintptr_t)audio_uart_nema_context_cell[0];
    return *(const volatile uint32_t *)(const volatile void *)(context + NEMA_CTX_TEX_WIDTH_OFFSET +
                                                               tex * NEMA_CTX_TEX_STRIDE);
}

enum {
    SCAN_FOUND,         /* next in-range stop found, segment starts at the previous one */
    SCAN_FOUND_LEADING, /* first in-range stop is > 0: implicit stop at 0 */
    SCAN_DESCENDING,    /* stops are not monotonic */
    SCAN_EXHAUSTED,
};

/* Inlined twice in stock (0x5fa290.. and 0x5fa3b6..). Walks the stops after
 * `index`, skipping values outside [0, 1]; n counts the effective stops. */
static int gradient_scan(int32_t count, const float *stops, int32_t index, int32_t prev_n,
                         int32_t *n_out, int32_t *found)
{
    int32_t n = prev_n;
    int32_t i;
    float prev;

    if (index == 0 && prev_n <= 1) {
        prev = GRADIENT_STOP_FLOOR;
        i = 0;
    } else {
        prev = stops[index];
        i = index + 1;
    }
    for (; i < count; i++) {
        float v = stops[i];
        if (v < prev) {
            *n_out = n;
            return SCAN_DESCENDING;
        }
        prev = v;
        if (v >= 0.0f && v <= 1.0f) {
            if (n != 0) {
                n++;
                if (n > 1) {
                    *n_out = n;
                    *found = i;
                    return SCAN_FOUND;
                }
            } else if (v > 0.0f) {
                *n_out = 2;
                *found = i;
                return SCAN_FOUND_LEADING;
            } else {
                n = 1;
            }
        }
    }
    *n_out = n;
    return SCAN_EXHAUSTED;
}

/* lv_ambiq_gradient_create(stops_count, stops, colors, tex): renders the
 * multi-stop gradient into row 0 of texture `tex`, one hardware-interpolated
 * fill per segment, then writes the first and last colours to x = 0 and
 * x = 63. Non-monotonic or empty stop lists draw a black-to-white ramp. */
void lv_ambiq_gradient_create_5fa238(int32_t count, const float *stops,
                                     const g2_color_var_t *colors, uint32_t tex)
{
    const uint32_t width = nema_texture_width(tex);
    int32_t index = 0;
    int32_t n = 0;
    int32_t prev_n = 0;
    int32_t found = 0;
    int scan;

    audio_uart_display_graphics_target_4b1516(0, 0, width, 1u);
    display_driver_nema_mode_513924(NEMA_BL_SRC, tex, NEMA_NOTEX, NEMA_NOTEX);
    display_driver_nema_cache_4b1588(1u);

    /* Pass 1: validate the stop list and count effective stops. */
    for (;;) {
        scan = gradient_scan(count, stops, index, prev_n, &n, &found);
        if (scan == SCAN_DESCENDING)
            goto fallback;
        if (scan == SCAN_EXHAUSTED) {
            if (n > 0 && stops[index] < 1.0f)
                n++; /* implicit end stop at 1 */
            break;
        }
        if (n == prev_n)
            break;
        index = found;
        prev_n = n;
    }
    if (n == 0)
        goto fallback;

    /* Pass 2: draw each segment. */
    {
        float first_r = 0.0f, first_g = 0.0f, first_b = 0.0f, first_a = 0.0f;
        g2_color_var_t last = {0.0f, 0.0f, 0.0f, 0.0f};
        const float fw = (float)width;
        const float fw1 = (float)(width - 1u);
        int32_t cur = 0;
        int32_t prev_idx = 0;
        int32_t valid = 1;
        int32_t first = 1;

        prev_n = 0;
        for (;;) {
            const g2_color_var_t *ck;
            const g2_color_var_t *cj;
            int32_t k = 0, j = 0, m = 0, done, edge = 0;
            int32_t x0, span_px;
            float pos_k, pos_j, frac, span, off, t;
            float dr, dg, db, da, r, g, b, a;

            scan = gradient_scan(count, stops, cur, prev_n, &n, &found);
            if (scan == SCAN_FOUND_LEADING) {
                done = 0;
                k = found;
                j = found;
            } else if (scan == SCAN_FOUND) {
                done = 0;
                k = cur;
                j = found;
            } else if (scan == SCAN_DESCENDING) {
                valid = 0;
                done = 1;
                k = prev_idx;
                j = cur;
            } else if (valid == 0) {
                done = 1;
                k = prev_idx;
                j = cur;
            } else {
                done = valid;
                if (n > 0 && stops[cur] < 1.0f) {
                    n++;
                    if (n == prev_n)
                        break;
                    edge = 1;
                    m = cur;
                    j = cur;
                } else {
                    k = prev_idx;
                    j = cur;
                }
            }
            if (edge == 0) {
                if (n == prev_n)
                    break;
                if (k == j) {
                    edge = 1;
                    m = j;
                }
            }

            if (edge != 0 && n == 2) {
                /* Leading edge: solid colors[m] from x = 0. */
                ck = &colors[m];
                cj = ck;
                x0 = 0;
                span_px = (int32_t)(stops[m] * fw);
                t = fw1 * stops[m];
                pos_j = t + 0.5f;
                pos_k = 0.5f;
                frac = 0.5f;
                cur = j;
                prev_idx = j;
            } else if (edge != 0 && n > 2) {
                /* Trailing edge: solid colors[m] up to the texture end. */
                ck = &colors[m];
                cj = ck;
                x0 = (int32_t)(stops[m] * fw);
                t = fw1 * stops[m];
                pos_k = t + 0.5f;
                frac = pos_k - (float)(int32_t)pos_k;
                pos_j = fw - 0.5f;
                span_px = (int32_t)width - x0;
                cur = j;
                prev_idx = j;
            } else {
                if (edge != 0) {
                    /* n < 2: degenerate segment m..m. */
                    k = m;
                    j = m;
                    cur = j;
                    prev_idx = j;
                } else {
                    prev_idx = k;
                    cur = j;
                }
                ck = &colors[k];
                cj = &colors[j];
                x0 = (int32_t)(stops[k] * fw);
                t = stops[k] * fw1;
                pos_k = t + 0.5f;
                span_px = (int32_t)(stops[j] * fw);
                t = fw1 * stops[j];
                pos_j = t + 0.5f;
                frac = pos_k - (float)(int32_t)pos_k;
                span_px -= x0;
            }
            prev_n = n;
            last = *cj;

            span = pos_j - pos_k;
            dr = (cj->r - ck->r) / span;
            dg = (cj->g - ck->g) / span;
            db = (cj->b - ck->b) / span;
            da = (cj->a - ck->a) / span;
            /* Sample at the pixel centre of x0. */
            if (frac > 0.5f)
                off = 1.5f - frac;
            else
                off = 0.5f - frac;
            t = dr * off;
            r = t + ck->r;
            t = dg * off;
            g = t + ck->g;
            t = db * off;
            b = t + ck->b;
            t = da * off;
            a = t + ck->a;
            nema_set_gradient_4b199c(r, g, b, a, dr, 0.0f, dg, 0.0f, db, 0.0f, da, 0.0f);
            audio_uart_ambiq_label_fill_rectangle_4b1ab0((uint32_t)x0, 0u, (uint32_t)span_px, 1u,
                                                         0xffffffffu);
            if (first == 1) {
                first_r = r;
                first_g = g;
                first_b = b;
                first_a = a;
            }
            if (done == 1)
                break;
            first = done;
        }

        display_driver_nema_cache_4b1588(0u);
        audio_uart_ambiq_label_fill_rectangle_4b1ab0(
            0u, 0u, 1u, 1u,
            audio_uart_ambiq_color_pack_4b15a6((uint32_t)first_r & 0xffu, (uint32_t)first_g & 0xffu,
                                               (uint32_t)first_b & 0xffu, (uint32_t)first_a & 0xffu));
        audio_uart_ambiq_label_fill_rectangle_4b1ab0(
            GRADIENT_TEXTURE_LAST_X, 0u, 1u, 1u,
            audio_uart_ambiq_color_pack_4b15a6((uint32_t)last.r & 0xffu, (uint32_t)last.g & 0xffu,
                                               (uint32_t)last.b & 0xffu, (uint32_t)last.a & 0xffu));
        goto out;
    }

fallback:
    {
        const g2_color_var_t black = {0.0f, 0.0f, 0.0f, 255.0f};     /* pool 0x5fa4a0 */
        const g2_color_var_t white = {255.0f, 255.0f, 255.0f, 255.0f}; /* ROM 0x789f70 */
        nema_interpolate_rect_colors_5f9f14(0, 0, (int32_t)width, 1, &black, &white, &white);
        audio_uart_ambiq_label_fill_rectangle_4b1ab0(0u, 0u, width, 1u, 0xffffffffu);
    }
out:
    display_driver_nema_cache_4b1588(0u);
    audio_uart_display_graphics_finish_4b1548();
}

/* lv_ambiq_dashline_create(dash_width, dash_gap, color, tex): row 0 of `tex`
 * becomes `color` for the dash fraction of its width and transparent after. */
void lv_ambiq_dashline_create_5fa7c0(uint32_t dash_width, uint32_t dash_gap, uint32_t color,
                                     uint32_t tex)
{
    const uint32_t width = nema_texture_width(tex);
    float ratio;
    uint32_t dash;

    audio_uart_display_graphics_target_4b1516(0, 0, width, 1u);
    display_driver_nema_mode_513924(NEMA_BL_SRC, tex, NEMA_NOTEX, NEMA_NOTEX);
    ratio = (float)dash_width / (float)(dash_width + dash_gap);
    dash = (uint32_t)(ratio * (float)width);
    display_driver_nema_select_522a16(color);
    (void)audio_uart_nema_mask_rectangle_522ae0(0, 0, (int32_t)dash, 1);
    display_driver_nema_select_522a16(0u);
    (void)audio_uart_nema_mask_rectangle_522ae0((int32_t)dash, 0, (int32_t)(width - dash), 1);
    audio_uart_display_graphics_finish_4b1548();
}
