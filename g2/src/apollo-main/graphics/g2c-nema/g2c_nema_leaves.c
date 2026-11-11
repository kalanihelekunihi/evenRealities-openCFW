/* g2c wave 2: NemaGFX leaves decompiled from the 2.2.6.10 image, following
 * the existing g2 practice of reconstructing the statically linked NemaGFX
 * code (other nema leaves already live under graphics/ambiq-buffer-handlers).
 * Profile g2-apollo-main-1 (hard-float). */
#include <stdint.h>

typedef struct { float r, g, b, a; } g2c_color_var_t;

extern uint32_t *audio_uart_nema_cl_get_space_514aec(uint32_t);
extern volatile uint32_t audio_uart_nema_context_cell[1];     /* RAM 0x20074efc */
extern int32_t  nema_sys_init_513f9c(void);
extern uint32_t audio_uart_nema_reg_read_51403c(uint32_t);
extern void     audio_uart_nema_reg_write_514046(uint32_t, uint32_t);
extern void     audio_uart_nema_cl_unbind_5144ba(void);
extern void     audio_uart_lv_memzero_48949c(void *, uint32_t);
extern void     audio_uart_nema_child_523304(uint32_t);
extern void     audio_uart_nema_child_5138a4(void);
extern void     audio_uart_nema_child_514846(uint32_t, uint32_t);
extern uint32_t audio_uart_nema_child_522602(void);
extern void     audio_uart_nema_child_52296a(uint32_t);
extern void     audio_uart_nema_child_52262e(uint32_t);
extern uint32_t audio_uart_nema_child_52261a(void);

/* Stock 0x005242cc nema_f2fx: float -> 16.16 fixed (x * 65536.0f + 0.5). */
static int32_t g2c_nema_f2fx(float x) { return (int32_t)(x * 65536.0f + 0.5f); }

/* Stock 0x00522974 nema_set_gradient_fx: 12 register writes 0x1c0..0x1cc,
 * 0x1a0..0x1bc in one 0xc-pair command-list chunk. */
void nema_set_gradient_fx_522974(int32_t r, int32_t g, int32_t b, int32_t a,
                                 int32_t drdx, int32_t drdy, int32_t dgdx, int32_t dgdy,
                                 int32_t dbdx, int32_t dbdy, int32_t dadx, int32_t dady)
{
    uint32_t *c = audio_uart_nema_cl_get_space_514aec(0xcu);
    if (c == 0)
        return;
    c[0]  = 0x1c0u; c[1]  = (uint32_t)r;
    c[2]  = 0x1c4u; c[3]  = (uint32_t)g;
    c[4]  = 0x1c8u; c[5]  = (uint32_t)b;
    c[6]  = 0x1ccu; c[7]  = (uint32_t)a;
    c[8]  = 0x1a0u; c[9]  = (uint32_t)drdx;
    c[10] = 0x1a4u; c[11] = (uint32_t)drdy;
    c[12] = 0x1a8u; c[13] = (uint32_t)dgdx;
    c[14] = 0x1acu; c[15] = (uint32_t)dgdy;
    c[16] = 0x1b0u; c[17] = (uint32_t)dbdx;
    c[18] = 0x1b4u; c[19] = (uint32_t)dbdy;
    c[20] = 0x1b8u; c[21] = (uint32_t)dadx;
    c[22] = 0x1bcu; c[23] = (uint32_t)dady;
}

/* Stock 0x004b199c nema_set_gradient. */
void nema_set_gradient_4b199c(float r, float g, float b, float a,
                              float drdx, float drdy, float dgdx, float dgdy,
                              float dbdx, float dbdy, float dadx, float dady)
{
    nema_set_gradient_fx_522974(g2c_nema_f2fx(r), g2c_nema_f2fx(g), g2c_nema_f2fx(b),
                                g2c_nema_f2fx(a), g2c_nema_f2fx(drdx), g2c_nema_f2fx(drdy),
                                g2c_nema_f2fx(dgdx), g2c_nema_f2fx(dgdy), g2c_nema_f2fx(dbdx),
                                g2c_nema_f2fx(dbdy), g2c_nema_f2fx(dadx), g2c_nema_f2fx(dady));
}

/* Stock 0x005f9f14 nema_interpolate_rect_colors: col0 at (x0,y0), col1 one
 * width to the right, col2 one height below col1; x0/y0 are unused. */
void nema_interpolate_rect_colors_5f9f14(int32_t x0, int32_t y0, int32_t w, int32_t h,
                                         const g2c_color_var_t *c0,
                                         const g2c_color_var_t *c1,
                                         const g2c_color_var_t *c2)
{
    (void)x0; (void)y0;
    float fw = (float)w, fh = (float)h;
    nema_set_gradient_4b199c(c0->r, c0->g, c0->b, c0->a,
                             (c1->r - c0->r) / fw, (c2->r - c1->r) / fh,
                             (c1->g - c0->g) / fw, (c2->g - c1->g) / fh,
                             (c1->b - c0->b) / fw, (c2->b - c1->b) / fh,
                             (c1->a - c0->a) / fw, (c2->a - c1->a) / fh);
}

/* Default NEMA context, stock RAM 0x200709ec (returned by 0x5225fc).
 * Size 0x100: stock nema_init zeroes 256 B (0x4b110e mov.w r1,#256; bl 0x48949c).
 * A full-image literal scan of 0x20070900..0x20070c40 finds the next referenced RAM
 * object at 0x20070aec = 0x200709ec + 0x100 (11 refs), so the object is exactly 0x100 (wave20). */
uint32_t g2c_nema_default_context_200709ec[0x100u / 4u] __attribute__((aligned(8)));

/* Stock 0x004b10c0 nema_init. 0x86362000 is the expected NEMA ID register
 * value at offset 0x1ec. */
int32_t nema_init_4b10c0(void)
{
    volatile uint8_t *ctx = (volatile uint8_t *)g2c_nema_default_context_200709ec;
    audio_uart_nema_context_cell[0] = (uint32_t)(uintptr_t)ctx;

    int32_t rc = nema_sys_init_513f9c();
    if (rc < 0) {
        *(volatile uint32_t *)(ctx + 0x20) |= 1u;
        return rc;
    }
    if (audio_uart_nema_reg_read_51403c(0x1ecu) != 0x86362000u) {
        *(volatile uint32_t *)(ctx + 0x20) |= 2u;
        return -1;
    }
    audio_uart_nema_cl_unbind_5144ba();
    audio_uart_lv_memzero_48949c((void *)ctx, 0x100u);
    if (rc == 0) {
        audio_uart_nema_reg_write_514046(0xe8u, 0u);
        audio_uart_nema_reg_write_514046(0xfcu, 0u);
        audio_uart_nema_reg_write_514046(0x388u, 1u);
        audio_uart_nema_child_523304(0u);
        audio_uart_nema_child_5138a4();
        audio_uart_nema_child_514846(0x200u, 0u);
        audio_uart_nema_child_514846(0x204u, 0xffffffffu);
        if (audio_uart_nema_child_522602() & (1u << 18)) {
            audio_uart_nema_child_52296a(7u);
            ctx[9] = 0u;
            audio_uart_nema_child_52262e((uint32_t)(ctx[8] | ctx[9]));
        } else {
            ctx[10] = 0u;
        }
        *(volatile uint32_t *)(ctx + 0x14) = 0u;
        *(volatile uint32_t *)(ctx + 0x18) = *(volatile uint32_t *)(ctx + 0x0c) |
                                             *(volatile uint32_t *)(ctx + 0x10) |
                                             *(volatile uint32_t *)(ctx + 0x1c);
        if (audio_uart_nema_child_52261a() & (1u << 9)) {
            audio_uart_nema_reg_write_514046(0x374u, 0u);
            audio_uart_nema_reg_write_514046(0x368u, 0u);
        }
    }
    return 0;
}
