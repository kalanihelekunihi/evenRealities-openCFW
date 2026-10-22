/* Navigation UI rotated compass image, part of stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\navigation\navigation_ui.c (log tag
 * "navigation.ui", ROM 0x787ab0). Native 0x54e44c..0x54e5d7
 * (navigation_create_rotated_img) and 0x54e660..0x54ed35
 * (navigation_update_rotated_img); literal pools 0x54e5d8..0x54e65f and
 * 0x54ed38..0x54ee17 (shared with the mode-select functions).
 *
 * The rotation is done in software on the CPU: the 4- or 8-bit BMP is converted to
 * L8 grey levels (170x170 expected), rotated about (85, 85) by angle/10 degrees with
 * nearest-neighbour sampling into a white canvas, and the centre 120x120 is copied
 * out and shown through an L8 lv_image_dsc_t. Needs the hard-float profile
 * (g2-apollo-main-3). */
#include <stdint.h>
#include <stddef.h>

#define ROT_SRC 170          /* 0xaa: decoded / rotated canvas edge */
#define ROT_CENTER 85.0f     /* ROM 0x54ec28 */
#define ROT_OUT 120          /* 0x78: shown image edge */
#define ROT_CROP ((ROT_SRC - ROT_OUT) / 2)
#define ROT_PI 3.14159f      /* ROM 0x54ec20 */
#define ROT_DECIDEG_HALF_TURN 1800.0f /* ROM 0x54ec24 */
#define NAV_BMP_SIGNATURE 0x4d42u

#define LV_IMAGE_HEADER_MAGIC 0x19u
#define LV_COLOR_FORMAT_L8 0x06u

#define LOG_FLAGS(level, nargs) (((uint32_t)(level) << 26) | ((uint32_t)(nargs) << 22))

/* Windows BMP file + info header. */
typedef struct __attribute__((packed)) {
    uint16_t signature;                  /* +0x00 */
    uint32_t file_size;                  /* +0x02 */
    uint32_t reserved;                   /* +0x06 */
    uint32_t data_offset;                /* +0x0a */
    uint32_t info_size;                  /* +0x0e */
    int32_t width;                       /* +0x12 */
    int32_t height;                      /* +0x16 >0: bottom-up rows */
    uint16_t planes;                     /* +0x1a */
    uint16_t bit_count;                  /* +0x1c */
    uint32_t compression;                /* +0x1e */
    uint32_t image_size;                 /* +0x22 */
    int32_t x_ppm;                       /* +0x26 */
    int32_t y_ppm;                       /* +0x2a */
    uint32_t colors_used;                /* +0x2e 0 = 1 << bit_count */
    uint32_t colors_important;           /* +0x32 */
    uint8_t palette[1][4];               /* +0x36 {blue, green, red, 0} */
} nav_rot_bmp_header_t;
_Static_assert(offsetof(nav_rot_bmp_header_t, palette) == 0x36, "bmp header");

/* LVGL 9 lv_image_header_t / lv_image_dsc_t. */
typedef struct {
    uint32_t magic : 8;
    uint32_t cf : 8;
    uint32_t flags : 16;
    uint32_t w : 16;
    uint32_t h : 16;
    uint32_t stride : 16;
    uint32_t reserved_2 : 16;
} nav_rot_image_header_t;

typedef struct {
    nav_rot_image_header_t header;       /* +0x00 */
    uint32_t data_size;                  /* +0x0c */
    const uint8_t *data;                 /* +0x10 */
    const void *reserved;                /* +0x14 */
    const void *reserved_2;              /* +0x18 */
} nav_rot_image_dsc_t;
_Static_assert(sizeof(nav_rot_image_dsc_t) == 0x1c, "lv_image_dsc_t");

extern uint8_t g2_nav_rotated_img_gray_2030b400[ROT_SRC * ROT_SRC];    /* RAM 0x2030b400 decoded L8 */
extern uint8_t g2_nav_rotated_img_canvas_20312500[ROT_SRC * ROT_SRC];  /* RAM 0x20312500 rotated */
extern uint8_t g2_nav_rotated_img_out_20339bb0[ROT_OUT * ROT_OUT];     /* RAM 0x20339bb0 shown pixels */
extern nav_rot_image_dsc_t g2_nav_rotated_img_dsc_20073ac8;            /* RAM 0x20073ac8 */

/* LVGL 9 (stock copies). lv_color_t {blue, green, red} travels in r0. */
extern void audio_uart_page_43f09a(void *obj, int32_t x, int32_t y);        /* lv_obj_set_pos */
extern void audio_uart_page_43f4c0(void *obj, int32_t w, int32_t h);        /* lv_obj_set_size */
extern void audio_uart_page_invalidate_440656(void *obj);                   /* lv_obj_invalidate */
extern uint32_t audio_uart_page_441068(uint32_t r, uint32_t g, uint32_t b); /* lv_color_make */
extern void *audio_uart_page_498668(void *parent);                          /* lv_image_create */
extern void audio_uart_page_498680(void *obj, const void *src);             /* lv_image_set_src */

/* Same TU (segment a-47) and page manager. */
extern uint8_t color_to_gray_5456d6(uint32_t color);
extern void *display_page_root_obj_get_45fe04(void *manager);
/* navigation_data_handler.c getters. */
extern void *navigation_page_manager_get_585cba(void);     /* RAM word 0x20074720 */
extern uint8_t navigation_foreground_layer_active_585cc2(void); /* RAM byte 0x20074fe6 */

/* Runtime. */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern uint32_t audio_uart_cache_clean_range_47510e(const uint32_t *range); /* {addr, size} */
extern int32_t iar_abs_509694(int32_t v);
extern __attribute__((pcs("aapcs-vfp"))) float audio_uart_float_trig_mode1_50968c(float); /* cosf */
extern __attribute__((pcs("aapcs-vfp"))) float audio_uart_float_trig_mode0_509690(float); /* sinf */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *,
                               ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

void *navigation_create_rotated_img_54e44c(void *parent, int32_t w, int32_t h, int32_t x, int32_t y);
int32_t navigation_update_rotated_img_54e660(void *img, const uint8_t *bmp, int32_t w, int32_t h,
                                             int32_t angle, uint32_t bpp);

static const char module_tag[] = "navigation.ui"; /* ROM 0x787ab0 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\navigation\\navigation_ui.c"; /* ROM 0x6fb6e4 */

#define NAV_LOG(level, fn, line, cflags, msg, msg_short, ...)                                        \
    do {                                                                                            \
        if ((audio_log_flags() & 2u) != 0u)                                                         \
            audio_log_extended((level), module_tag, source_file, (fn), (line), (msg), ##__VA_ARGS__); \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                       \
            (void)compress_log_output((cflags), (msg_short), (msg_short), ##__VA_ARGS__);            \
    } while (0)

static const char fn_create[] = "navigation_create_rotated_img"; /* ROM 0x7627f0 */
static const char bad_parent[] = "Invalid parent object"; /* ROM 0x7798ec */
static const char bad_parent_s[] = "[navigation.ui]Invalid parent object"; /* ROM 0x74b5a4 */
static const char no_image[] = "Failed to create image object for rotated image"; /* ROM 0x735cb4 */
static const char no_image_s[] = "[navigation.ui]Failed to create image object for rotated image"; /* ROM 0x70d2e4 */
static const char size_mismatch[] = "Display size mismatch: expected %dx%d, got %dx%d"; /* ROM 0x72b438 */
static const char size_mismatch_s[] = "[navigation.ui]Display size mismatch: expected %dx%d, got %dx%d"; /* ROM 0x70d324 */
static const char created[] = "Created rotated image object: %dx%d at (%d,%d)"; /* ROM 0x735ce4 */
static const char created_s[] = "[navigation.ui]Created rotated image object: %dx%d at (%d,%d)"; /* ROM 0x70d364 */

static const char fn_update[] = "navigation_update_rotated_img"; /* ROM 0x762810 */
static const char bad_params[] = "Invalid parameters for updating rotated image"; /* ROM 0x735d14 */
static const char bad_params_s[] = "[navigation.ui]Invalid parameters for updating rotated image"; /* ROM 0x70d3a4 */
static const char bad_signature[] = "Invalid BMP signature"; /* ROM 0x779904 */
static const char bad_signature_s[] = "[navigation.ui]Invalid BMP signature"; /* ROM 0x74b5cc */
static const char depth_mismatch[] = "BMP bit depth mismatch: expected %d-bit, got %d-bit"; /* ROM 0x72b46c */
static const char depth_mismatch_s[] =
    "[navigation.ui]BMP bit depth mismatch: expected %d-bit, got %d-bit"; /* ROM 0x704280 */
static const char depth_unsupported[] = "Unsupported bit depth: %d (only 4-bit and 8-bit supported)"; /* ROM 0x716c90 */
static const char depth_unsupported_s[] =
    "[navigation.ui]Unsupported bit depth: %d (only 4-bit and 8-bit supported)"; /* ROM 0x6f4d24 */
static const char bmp_size_mismatch[] = "BMP size mismatch: expected %dx%d, got %dx%d"; /* ROM 0x735924 */
static const char bmp_size_mismatch_s[] = "[navigation.ui]BMP size mismatch: expected %dx%d, got %dx%d"; /* ROM 0x7165c4 */
static const char colors_used[] = "info_header->colors_used: %d"; /* ROM 0x762830 */
static const char colors_used_s[] = "[navigation.ui]info_header->colors_used: %d"; /* ROM 0x74083c */
static const char palette_size_msg[] = "palette_size: %d"; /* ROM 0x781444 */
static const char palette_size_msg_s[] = "[navigation.ui]palette_size: %d"; /* ROM 0x762850 */
/* "Foreground layer active, refresh the whole container to keep the layer order right". */
static const char refresh_root[] = "有前景层活动，刷新整个容器以确保层级正确"; /* ROM 0x70d3e4 */
static const char refresh_root_s[] = "[navigation.ui]有前景层活动，刷新整个容器以确保层级正确"; /* ROM 0x6f4d70 */
/* "Failed to get the root container, falling back to a normal refresh". */
static const char no_root[] = "获取根容器失败，降级为常规刷新"; /* ROM 0x735d44 */
static const char no_root_s[] = "[navigation.ui]获取根容器失败，降级为常规刷新"; /* ROM 0x70d424 */
/* "page_manager not initialised, falling back to a normal refresh". */
static const char no_manager[] = "page_manager 未初始化，降级为常规刷新"; /* ROM 0x72b4a0 */
static const char no_manager_s[] = "[navigation.ui]page_manager 未初始化，降级为常规刷新"; /* ROM 0x7042c4 */
/* "No foreground layer active, refresh only the map object (performance)". */
static const char refresh_img[] = "无前景层活动，仅刷新地图对象（性能优化）"; /* ROM 0x70d464 */
static const char refresh_img_s[] = "[navigation.ui]无前景层活动，仅刷新地图对象（性能优化）"; /* ROM 0x6f4dbc */
/* "CPU software rotation". */
static const char rotated[] = "CPU软件旋转: rotated %dx%d -> extracted %dx%d, rotation %d/10 degrees"; /* ROM 0x6f4e08 */
static const char rotated_s[] =
    "[navigation.ui]CPU软件旋转: rotated %dx%d -> extracted %dx%d, rotation %d/10 degrees"; /* ROM 0x6e0fe0 */
static const char samples[] = "Extracted pixel samples: first=%d, center=%d, last=%d"; /* ROM 0x720910 */
static const char samples_s[] =
    "[navigation.ui]Extracted pixel samples: first=%d, center=%d, last=%d"; /* ROM 0x6fbad4 */

void *navigation_create_rotated_img_54e44c(void *parent, int32_t w, int32_t h, int32_t x, int32_t y)
{
    void *img;

    if (parent == NULL) {
        NAV_LOG(1, fn_create, 0xf07u, LOG_FLAGS(1, 0), bad_parent, bad_parent_s);
        return NULL;
    }
    img = audio_uart_page_498668(parent);
    if (img == NULL) {
        NAV_LOG(1, fn_create, 0xf0eu, LOG_FLAGS(1, 0), no_image, no_image_s);
        return NULL;
    }
    if (w != ROT_OUT || h != ROT_OUT)
        NAV_LOG(2, fn_create, 0xf15u, LOG_FLAGS(2, 4), size_mismatch, size_mismatch_s, ROT_OUT, ROT_OUT, w, h);
    audio_uart_page_43f4c0(img, w, h);
    audio_uart_page_43f09a(img, x, y);
    audio_uart_page_498680(img, NULL);
    NAV_LOG(4, fn_create, 0xf24u, LOG_FLAGS(4, 4), created, created_s, w, h, x, y);
    return img;
}

/* bmp: 4- or 8-bit palette BMP of w x h (170x170 expected); angle in 1/10 degree. */
int32_t navigation_update_rotated_img_54e660(void *img, const uint8_t *bmp, int32_t w, int32_t h,
                                             int32_t angle, uint32_t bpp)
{
    const nav_rot_bmp_header_t *hdr = (const nav_rot_bmp_header_t *)(const void *)bmp;
    const uint8_t *palette;
    const uint8_t *pixels;
    uint32_t palette_size;
    int32_t stride;
    float rad;
    float c;
    float s;
    uint32_t range[2];
    nav_rot_image_dsc_t *dsc = &g2_nav_rotated_img_dsc_20073ac8;
    uint8_t *out = g2_nav_rotated_img_out_20339bb0;
    void *manager;
    void *root;

    if (img == NULL || bmp == NULL) {
        NAV_LOG(1, fn_update, 0xf3cu, LOG_FLAGS(1, 0), bad_params, bad_params_s);
        return -1;
    }
    if (hdr->signature != NAV_BMP_SIGNATURE) {
        NAV_LOG(1, fn_update, 0xf43u, LOG_FLAGS(1, 0), bad_signature, bad_signature_s);
        return -1;
    }
    if (hdr->bit_count != bpp) {
        NAV_LOG(1, fn_update, 0xf4bu, LOG_FLAGS(1, 2), depth_mismatch, depth_mismatch_s, bpp,
                (uint32_t)hdr->bit_count);
        return -1;
    }
    if (bpp != 4u && bpp != 8u) {
        NAV_LOG(1, fn_update, 0xf50u, LOG_FLAGS(1, 1), depth_unsupported, depth_unsupported_s, bpp);
        return -1;
    }
    if (hdr->width != w || iar_abs_509694(hdr->height) != h)
        NAV_LOG(2, fn_update, 0xf57u, LOG_FLAGS(2, 4), bmp_size_mismatch, bmp_size_mismatch_s, w, h, hdr->width,
                iar_abs_509694(hdr->height));
    NAV_LOG(3, fn_update, 0xf5du, LOG_FLAGS(3, 1), colors_used, colors_used_s, hdr->colors_used);
    if (bpp == 4u)
        palette_size = hdr->colors_used == 0u ? 16u : hdr->colors_used;
    else
        palette_size = hdr->colors_used == 0u ? 256u : hdr->colors_used;
    NAV_LOG(3, fn_update, 0xf63u, LOG_FLAGS(3, 1), palette_size_msg, palette_size_msg_s, palette_size);

    /* Palette BMP -> L8 grey, rows top-down, w bytes per row. */
    palette = bmp + offsetof(nav_rot_bmp_header_t, palette);
    pixels = bmp + hdr->data_offset;
    stride = (bpp == 4u) ? (((w + 1) / 2 + 3) / 4) * 4 : ((w + 3) / 4) * 4;
    for (int32_t yy = 0; yy < h; yy++) {
        for (int32_t xx = 0; xx < w; xx++) {
            int32_t row = hdr->height > 0 ? (h - 1) - yy : yy;
            uint8_t index;
            if (bpp == 4u) {
                uint8_t b = pixels[stride * row + xx / 2];
                index = (xx & 1) ? (uint8_t)(b & 0xfu) : (uint8_t)(b >> 4);
            } else {
                index = pixels[stride * row + xx];
            }
            if (index >= palette_size)
                index = 0u;
            g2_nav_rotated_img_gray_2030b400[w * yy + xx] = color_to_gray_5456d6(
                audio_uart_page_441068(palette[index * 4u + 2u], palette[index * 4u + 1u], palette[index * 4u]));
        }
    }

    /* Inverse-map every canvas pixel into the source (nearest neighbour); white fill. */
    (void)aeabi_memset_43c0e4(g2_nav_rotated_img_canvas_20312500, sizeof g2_nav_rotated_img_canvas_20312500, 0xff);
    rad = ((float)angle * ROT_PI) / ROT_DECIDEG_HALF_TURN;
    c = audio_uart_float_trig_mode1_50968c(rad);
    s = audio_uart_float_trig_mode0_509690(rad);
    for (int32_t yy = 0; yy < ROT_SRC; yy++) {
        for (int32_t xx = 0; xx < ROT_SRC; xx++) {
            float dx = (float)xx - ROT_CENTER;
            float dy = (float)yy - ROT_CENTER;
            int32_t sx = (int32_t)(dx * c + dy * s + ROT_CENTER);
            int32_t sy = (int32_t)(dy * c - dx * s + ROT_CENTER);
            if ((uint32_t)sx < ROT_SRC && (uint32_t)sy < ROT_SRC)
                g2_nav_rotated_img_canvas_20312500[yy * ROT_SRC + xx] =
                    g2_nav_rotated_img_gray_2030b400[sy * ROT_SRC + sx];
        }
    }
    for (int32_t yy = 0; yy < ROT_OUT; yy++)
        for (int32_t xx = 0; xx < ROT_OUT; xx++)
            out[yy * ROT_OUT + xx] = g2_nav_rotated_img_canvas_20312500[(yy + ROT_CROP) * ROT_SRC + xx + ROT_CROP];

    range[0] = (uint32_t)(uintptr_t)out;
    range[1] = ROT_OUT * ROT_OUT;
    (void)audio_uart_cache_clean_range_47510e(range);
    (void)aeabi_memset_43c0e4(dsc, sizeof *dsc, 0);
    dsc->header.magic = LV_IMAGE_HEADER_MAGIC;
    dsc->header.cf = LV_COLOR_FORMAT_L8;
    dsc->header.w = ROT_OUT;
    dsc->header.h = ROT_OUT;
    dsc->header.stride = ROT_OUT;
    dsc->header.flags = 0u;
    dsc->data_size = ROT_OUT * ROT_OUT;
    dsc->data = out;
    dsc->reserved = NULL;
    dsc->reserved_2 = NULL;
    audio_uart_page_498680(img, dsc);

    /* With a foreground layer on top, invalidate the whole page root so the layers
     * are redrawn in order; otherwise only the image. */
    if (navigation_foreground_layer_active_585cc2() == 0u) {
        audio_uart_page_invalidate_440656(img);
        NAV_LOG(4, fn_update, 0xffdu, LOG_FLAGS(4, 0), refresh_img, refresh_img_s);
    } else if ((manager = navigation_page_manager_get_585cba()) == NULL) {
        audio_uart_page_invalidate_440656(img);
        NAV_LOG(4, fn_update, 0xff8u, LOG_FLAGS(4, 0), no_manager, no_manager_s);
    } else if ((root = display_page_root_obj_get_45fe04(manager)) == NULL) {
        audio_uart_page_invalidate_440656(img);
        NAV_LOG(4, fn_update, 0xff3u, LOG_FLAGS(4, 0), no_root, no_root_s);
    } else {
        audio_uart_page_invalidate_440656(root);
        NAV_LOG(4, fn_update, 0xfefu, LOG_FLAGS(4, 0), refresh_root, refresh_root_s);
    }
    NAV_LOG(4, fn_update, 0x1002u, LOG_FLAGS(4, 5), rotated, rotated_s, w, h, ROT_OUT, ROT_OUT, angle);
    NAV_LOG(4, fn_update, 0x1004u, LOG_FLAGS(4, 3), samples, samples_s, out[0], out[ROT_OUT * ROT_OUT / 2],
            out[ROT_OUT * ROT_OUT - 1]);
    return 0;
}
