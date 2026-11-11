/* g2c: NemaGFX raster/matrix entry points reconstructed from the stock image
 * (no NemaGFX source is publicly available; see ledger). Each function names
 * its stock address. Command-list register words and the 0xff000100 trigger
 * word are taken verbatim from the stock literals; the NEMA context lives at
 * RAM 0x20074efc (audio_uart_nema_context_cell). Public names follow
 * nema_raster.h / nema_matrix3x3.h / nema_math.h so the upstream
 * ambiq-lvgl draw units bind to them via sources.json defsyms. */
#include <stdint.h>

extern volatile uint32_t audio_uart_nema_context_cell[1];
extern uint32_t *audio_uart_nema_cl_get_space_514aec(uint32_t pairs);
extern void audio_uart_nema_error_set_4b127c(uint32_t);
extern int32_t audio_uart_nema_extend_bound_514504(void);
extern int32_t audio_uart_nema_float_fixed_5242cc(float);
extern float audio_uart_nema_sin_52405c(float);
extern float audio_uart_nema_cos_524130(float);

#define G2C_NEMA_TRIGGER 0xff000100u
#define CTX() ((volatile uint32_t *)(uintptr_t)audio_uart_nema_context_cell[0])
#define F2FX audio_uart_nema_float_fixed_5242cc

/* Evidence: FUN_00514d2c @ 0x514d2c (102 B sha 9d168de3…), corpus decomp
 * returns 0/-1/-2; name nema_cl_enough_space from Nema API. Returns 0 if the bound
 * list has room (or could be extended), negative after setting an error. */
int32_t g2c_nema_cl_enough_space_514d2c(int32_t words) {
    volatile uint32_t *cl = (volatile uint32_t *)(uintptr_t)CTX()[1];
    if (!cl) { audio_uart_nema_error_set_4b127c(0x80u); return -2; }
    uint32_t flags = cl[6];
    if ((flags & 0x20u) == 0u && ((int32_t)cl[4] - (int32_t)cl[5]) / 2 <= words) {
        if (flags & 2u) {
            if (audio_uart_nema_extend_bound_514504() >= 0) return 0;
            audio_uart_nema_error_set_4b127c(0x10u);
        } else {
            audio_uart_nema_error_set_4b127c(8u);
        }
        return -1;
    }
    return 0;
}

static void emit_rect(uint32_t x0, uint32_t y0, uint32_t x1, uint32_t y1, uint32_t op) {
    uint32_t *c = audio_uart_nema_cl_get_space_514aec(3u);
    if (!c) return;
    c[0] = 0x104u; c[1] = (x0 & 0xffffu) | (y0 << 16);
    c[2] = 0x108u; c[3] = (x1 & 0xffffu) | (y1 << 16);
    c[4] = G2C_NEMA_TRIGGER; c[5] = CTX()[6] | op;
}

/* 0x522848: nema_set_matrix_all(m[3][3]); row-major float words. */
void g2c_nema_set_matrix_all_522848(const uint32_t m[9]) {
    uint32_t *c = audio_uart_nema_cl_get_space_514aec(9u);
    if (!c) return;
    c[0] = 0x174u; c[1] = m[5];  c[2] = 0x168u; c[3] = m[2];
    c[4] = 0x178u; c[5] = m[6];  c[6] = 0x17cu; c[7] = m[7];
    c[8] = 0x180u; c[9] = m[8];  c[10] = 0x160u; c[11] = m[0];
    c[12] = 0x164u; c[13] = m[1]; c[14] = 0x16cu; c[15] = m[3];
    c[16] = 0x170u; c[17] = m[4];
}

/* 0x522b30: nema_raster_rounded_rect(x, y, w, h, r). Midpoint circle split
 * into a centre rect plus horizontal spans. */
void g2c_nema_raster_rounded_rect_522b30(int32_t x, int32_t y, int32_t w, int32_t h, int32_t r) {
    if (w / 2 < r) r = w / 2;
    if (h / 2 < r) r = h / 2;
    if (r < 1) {
        if (w > 0 && h > 0) emit_rect((uint32_t)x, (uint32_t)y, (uint32_t)(x + w), (uint32_t)(y + h), 2u);
        return;
    }
    int32_t d0 = 3 - 2 * r, mid_h = h - 2 * r;
    /* dry run: count command words */
    int32_t words = mid_h >= 1 ? 3 : 0, i = 0, rr = r, d = d0;
    for (;;) {
        if (d < 0) d += i * 4 + 6;
        else { if (i != rr) words += 6; d += (i - rr) * 4 + 10; rr--; }
        i++;
        if (rr < i) break;
        if (i != 0) words += 6;
    }
    if (g2c_nema_cl_enough_space_514d2c(words) < 0) return;
    int32_t cx = x + r, cy = y + r, by = (y + h) - r - 1, rx = (x + w) - r - 1;
    if (mid_h >= 1 && w > 0)
        emit_rect((uint32_t)x, (uint32_t)cy, (uint32_t)(x + w), (uint32_t)(mid_h + cy), 2u);
    d = d0; rr = r;
    for (i = 0;;) {
        if (d < 0) d += i * 4 + 6;
        else {
            if (i != rr) {
                emit_rect((uint32_t)(cx - i), (uint32_t)(cy - rr), (uint32_t)(i + rx), (uint32_t)(cy - rr), 1u);
                emit_rect((uint32_t)(cx - i), (uint32_t)(rr + by), (uint32_t)(i + rx), (uint32_t)(rr + by), 1u);
            }
            d += (i - rr) * 4 + 10;
            rr--;
        }
        i++;
        if (rr < i) break;
        if (i != 0) {
            emit_rect((uint32_t)(cx - rr), (uint32_t)(cy - i), (uint32_t)(rr + rx), (uint32_t)(cy - i), 1u);
            emit_rect((uint32_t)(cx - rr), (uint32_t)(i + by), (uint32_t)(rr + rx), (uint32_t)(i + by), 1u);
        }
    }
}

/* 0x522a24: nema_raster_triangle_f(x0,y0,x1,y1,x2,y2). */
void g2c_nema_raster_triangle_f_522a24(float x0, float y0, float x1, float y1, float x2, float y2) {
    int32_t a = F2FX(x0), b = F2FX(y0), c2 = F2FX(x1), d = F2FX(y1), e = F2FX(x2), f = F2FX(y2);
    uint32_t *c = audio_uart_nema_cl_get_space_514aec(7u);
    if (!c) return;
    c[0] = 0x120u; c[1] = (uint32_t)a; c[2] = 0x124u; c[3] = (uint32_t)b;
    c[4] = 0x130u; c[5] = (uint32_t)c2; c[6] = 0x134u; c[7] = (uint32_t)d;
    c[8] = 0x140u; c[9] = (uint32_t)e; c[10] = 0x144u; c[11] = (uint32_t)f;
    c[12] = G2C_NEMA_TRIGGER;
    uint32_t v = CTX()[6];
    v = (v & 0x01000000u) ? (v | 0x00800000u) : (v & ~0x00800000u);
    c[13] = v | 4u;
}

/* 0x522e9c: nema_raster_quad_fx(x0..y3 fixed 16.16). */
void g2c_nema_raster_quad_fx_522e9c(int32_t x0, int32_t y0, int32_t x1, int32_t y1,
                                    int32_t x2, int32_t y2, int32_t x3, int32_t y3) {
    uint32_t *c = audio_uart_nema_cl_get_space_514aec(9u);
    if (!c) return;
    c[0] = 0x120u; c[1] = (uint32_t)x0; c[2] = 0x124u; c[3] = (uint32_t)y0;
    c[4] = 0x130u; c[5] = (uint32_t)x1; c[6] = 0x134u; c[7] = (uint32_t)y1;
    c[8] = 0x140u; c[9] = (uint32_t)x2; c[10] = 0x144u; c[11] = (uint32_t)y2;
    c[12] = 0x150u; c[13] = (uint32_t)x3; c[14] = 0x154u; c[15] = (uint32_t)y3;
    c[16] = G2C_NEMA_TRIGGER; c[17] = CTX()[6] | 5u;
}

static void set_aa(volatile uint32_t *ctx, uint32_t v) {
    ctx[7] = v;
    ctx[6] = ctx[4] | ctx[5] | ctx[3] | v;
}

/* Shared body of 0x52330c (aa_mask = 0, never touched) and 0x523674.
 * Evidence: stock keeps two copies; behaviour is identical when mask == 0
 * except that 0x52330c never inspects the mask bits. */
static void stroked_arc(float x, float y, float r, float w, float a0, float a1,
                        uint32_t mask, int use_mask) {
    float r_in = r;
    if (r < 1.0f) r = 1.0f;
    if (w < 1.0f) w = 1.0f;
    float hw = w * 0.5f;
    if (hw + 0.5f >= r_in) r = hw;   /* stock vcmp s3,s2 uses the caller's r */
    if (a0 == a1) return;
    int32_t n = (int32_t)(r * 0.9424778819084167f + 0.5f);
    int32_t seg = n > 96 ? 96 : (n < 32 ? 32 : ((n + 15) & ~15));
    float da = a1 - a0;
    if (da < 0.0f) da = a0 - a1;
    float steps = ((float)seg * da) / 360.0f;
    int32_t count = (int32_t)steps + (((float)(int32_t)steps < steps) ? 1 : 0);
    float step = da / steps;
    int32_t words = 0;
    if (a0 <= a1) {
        float a = a0;
        do { a += step; words += 9; } while (!(a > a1));
    }
    if (g2c_nema_cl_enough_space_514d2c(words) < 0) return;
    float ro = r + hw, ri = r - hw;
    int32_t fx = F2FX(x), fy = F2FX(y);
    int32_t pxo = F2FX(ro * audio_uart_nema_cos_524130(a0)), pyo = F2FX(ro * audio_uart_nema_sin_52405c(a0));
    int32_t pxi = F2FX(ri * audio_uart_nema_cos_524130(a0)), pyi = F2FX(ri * audio_uart_nema_sin_52405c(a0));
    volatile uint32_t *ctx = CTX();
    uint32_t saved = ctx[7];
    set_aa(ctx, 0x2800000u);
    if (use_mask && (mask & 0x04000000u)) set_aa(ctx, 0x6800000u);
    float a = a0;
    for (int32_t i = 0; i < count; i++) {
        a += step;
        float an = a;
        if (i + 1 == count) {
            an = a1;
            if (use_mask && (mask & 0x01000000u))
                set_aa(CTX(), ((mask & 0x04000000u) && count == 1) ? 0x7800000u : 0x3800000u);
        }
        float c = audio_uart_nema_cos_524130(an), s = audio_uart_nema_sin_52405c(an);
        int32_t nxo = F2FX(c * ro), nyo = F2FX(s * ro), nxi = F2FX(c * ri), nyi = F2FX(s * ri);
        uint32_t *cm = audio_uart_nema_cl_get_space_514aec(9u);
        if (cm) {
            cm[0] = 0x120u; cm[1] = (uint32_t)(pxi + fx); cm[2] = 0x124u; cm[3] = (uint32_t)(pyi + fy);
            cm[4] = 0x130u; cm[5] = (uint32_t)(pxo + fx); cm[6] = 0x134u; cm[7] = (uint32_t)(pyo + fy);
            cm[8] = 0x140u; cm[9] = (uint32_t)(nxo + fx); cm[10] = 0x144u; cm[11] = (uint32_t)(nyo + fy);
            cm[12] = 0x150u; cm[13] = (uint32_t)(nxi + fx); cm[14] = 0x154u; cm[15] = (uint32_t)(nyi + fy);
            cm[16] = G2C_NEMA_TRIGGER; cm[17] = CTX()[6] | 5u;
        }
        set_aa(CTX(), 0x2800000u);
        pxo = nxo; pyo = nyo; pxi = nxi; pyi = nyi;
    }
    set_aa(CTX(), saved & 0x7800000u);
}

/* 0x52330c: nema_raster_stroked_arc_aa(x, y, r, w, start, end). */
void g2c_nema_raster_stroked_arc_aa_52330c(float x, float y, float r, float w, float a0, float a1) {
    stroked_arc(x, y, r, w, a0, a1, 0u, 0);
}

/* 0x523674: nema_raster_stroked_arc_aa_mask(..., aa_mask). */
void g2c_nema_raster_stroked_arc_aa_mask_523674(float x, float y, float r, float w, float a0,
                                                float a1, uint32_t aa_mask) {
    stroked_arc(x, y, r, w, a0, a1, aa_mask, 1);
}

/* 0x524260: nema_atan(x) in degrees, rational approximation. */
float g2c_nema_atan_524260(float x) {
    if (x >= -1.0f && x < 1.0000001192092896f)
        return (x * 57.295799255371094f) / (x * 0.2800000011920929f * x + 1.0f);
    float t = (x * 57.295799255371094f) / (0.2800000011920929f + x * x);
    if (x >= 1.0000001192092896f) return 90.0f - t;
    return -(t + 90.0f);
}
