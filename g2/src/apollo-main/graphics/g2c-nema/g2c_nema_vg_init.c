/* g2c: nema_vg_init_stencil_prealloc (stock 0x522400) and the NemaVG
 * context helpers it calls (0x5155d6, 0x515304, 0x5675b4, 0x5675a8),
 * reconstructed from the stock image. */
#include <stdint.h>


typedef struct { uint32_t words[4]; } g2c_nema_buffer_t;

extern volatile uint32_t audio_uart_nema_vg_context_cell;                 /* RAM 0x20074f04 */
extern volatile uint32_t audio_uart_nema_vg_framebuffer_context_cell_20074f08; /* RAM 0x20074f08 */
extern void audio_uart_nema_instruction_upload_522920(const uint32_t *, uint32_t, uint32_t);
extern void audio_uart_nema_child_514846(uint32_t, uint32_t);
extern void audio_uart_nema_vg_framebuffer_store_5155e4(uint32_t, uint32_t, g2c_nema_buffer_t);
extern void *audio_uart_nema_vg_framebuffer_get_51562e(void);
extern void audio_uart_nema_vg_set_error_51565c(uint32_t);
extern void audio_uart_nema_matrix_identity_561810(void *);
extern void *audio_uart_nema_vg_paint_create_515096(void);
extern void *audio_uart_nema_vg_path_create_514ebc(void);
extern void *audio_uart_nema_vg_grad_create_51510e(void);

/* Stock NemaVG context storage at RAM 0x2006cd30 (literal 0x5156b0).
 * Proven size: reset touches 0x000..0x38b, rounded to 0x390 (stock memzero span). */
uint32_t g2c_nema_vg_context_2006cd30[0x390 / 4] __attribute__((aligned(8)));

/* ROM 0x5225d4..0x5225fb, same records display_nema_vg_reinit.c uploads. */
static const uint32_t vg_records[5][2] = {
    {0x080c0182u, 0x8a9f5a24u}, {0x080c0182u, 0x8a9f5a34u}, {0x080c0182u, 0x8a8761c6u},
    {0x004e0002u, 0x800b0286u}, {0x0a980002u, 0x8081a046u},
};

/* 0x5155d6 */
void *g2c_nema_vg_context_get_5155d6(void) { return g2c_nema_vg_context_2006cd30; }

#define B(o) (*(volatile uint8_t *)(c + (o)))
#define W(o) (*(volatile uint32_t *)(void *)(c + (o)))

static void zero(uint8_t *c, uint32_t from, uint32_t to) { for (uint32_t i = from; i < to; i++) B(i) = 0u; }

/* 0x515304: full NemaVG context reset. Untouched stock gaps are preserved:
 * 0x22..0x23, 0xa1..0xa3, 0x1c3, 0x2cc..0x2d3, 0x2e3. */
void g2c_nema_vg_context_reset_515304(void) {
    uint8_t *c = (uint8_t *)(uintptr_t)audio_uart_nema_vg_context_cell;
    zero(c, 0x00, 0x22);
    zero(c, 0x24, 0x38);
    audio_uart_nema_matrix_identity_561810(c + 0x38);
    zero(c, 0x5c, 0xa1);
    W(0x74) = 0x3f800000u; B(0x7c) = 2u; W(0x84) = 0x501u; W(0x88) = 0x2000000u; W(0x8c) = 0x7800000u;
    audio_uart_nema_matrix_identity_561810(c + 0xa4);
    audio_uart_nema_matrix_identity_561810(c + 0xc8);
    audio_uart_nema_matrix_identity_561810(c + 0xec);
    zero(c, 0x110, 0x1c3);
    W(0x120) = 0xffffffffu; W(0x12c) = 0x3f800000u; W(0x130) = 0x3f800000u; W(0x134) = 0x3f800000u;
    B(0x1c0) = 1u;
    zero(c, 0x1c4, 0x2cc);
    zero(c, 0x2d4, 0x2e3);
    W(0x2d8) = 0x3f800000u; W(0x2dc) = 0x40800000u; B(0x2e5) = 1u; B(0x2e6) = 1u;
    zero(c, 0x2e4, 0x2e5);
    zero(c, 0x2e7, 0x38c);
}

/* Evidence: FUN_005675b4 @ 0x5675b4 (46 B sha ef4d72d4…), corpus decomp sets
 * paint/path/gradient ptrs + clip 800x600; name nema_vg_handle_init. */
void g2c_nema_vg_handles_init_5675b4(void) {
    void *paint = audio_uart_nema_vg_paint_create_515096();
    ((volatile uint32_t *)(uintptr_t)audio_uart_nema_vg_context_cell)[0x64 / 4] = (uint32_t)(uintptr_t)paint;
    void *path = audio_uart_nema_vg_path_create_514ebc();
    ((volatile uint32_t *)(uintptr_t)audio_uart_nema_vg_context_cell)[0x68 / 4] = (uint32_t)(uintptr_t)path;
    void *grad = audio_uart_nema_vg_grad_create_51510e();
    volatile uint32_t *ctx = (volatile uint32_t *)(uintptr_t)audio_uart_nema_vg_context_cell;
    ctx[0x6c / 4] = (uint32_t)(uintptr_t)grad;
    ctx[0x5c / 4] = 800u; ctx[0x60 / 4] = 600u; ctx[0x70 / 4] = 0u;
}

/* 0x5675a8 */
void g2c_nema_vg_set_size_5675a8(uint32_t w, uint32_t h) {
    volatile uint32_t *ctx = (volatile uint32_t *)(uintptr_t)audio_uart_nema_vg_context_cell;
    ctx[0x5c / 4] = w; ctx[0x60 / 4] = h;
}

/* 0x522400 */
void nema_vg_init_stencil_prealloc_522400(int32_t width, int32_t height, g2c_nema_buffer_t stencil) {
    audio_uart_nema_vg_context_cell = (uint32_t)(uintptr_t)g2c_nema_vg_context_get_5155d6();
    audio_uart_nema_instruction_upload_522920(vg_records[0], 1u, 0x16u);
    audio_uart_nema_instruction_upload_522920(vg_records[1], 1u, 0x17u);
    audio_uart_nema_child_514846(0x388u, 1u);
    audio_uart_nema_instruction_upload_522920(vg_records[2], 1u, 0x15u);
    audio_uart_nema_instruction_upload_522920(vg_records[3], 1u, 0x14u);
    audio_uart_nema_instruction_upload_522920(vg_records[4], 1u, 0x13u);
    audio_uart_nema_vg_framebuffer_store_5155e4((uint32_t)width, (uint32_t)height, stencil);
    audio_uart_nema_vg_framebuffer_context_cell_20074f08 =
        (uint32_t)(uintptr_t)audio_uart_nema_vg_framebuffer_get_51562e();
    audio_uart_nema_vg_context_cell = (uint32_t)(uintptr_t)g2c_nema_vg_context_get_5155d6();
    g2c_nema_vg_context_reset_515304();
    const uint8_t *fb = (const uint8_t *)(uintptr_t)audio_uart_nema_vg_framebuffer_context_cell_20074f08;
    /* stencil width/height (fb+0x10/+0x14) must be multiples of 4 */
    if ((fb[0x10] & 3u) != 0u || (fb[0x14] & 3u) != 0u)
        audio_uart_nema_vg_set_error_51565c(0x2000000u);
    g2c_nema_vg_handles_init_5675b4();
    fb = (const uint8_t *)(uintptr_t)audio_uart_nema_vg_framebuffer_context_cell_20074f08;
    g2c_nema_vg_set_size_5675a8(*(const uint32_t *)(const void *)(fb + 0x10),
                                *(const uint32_t *)(const void *)(fb + 0x14));
}
