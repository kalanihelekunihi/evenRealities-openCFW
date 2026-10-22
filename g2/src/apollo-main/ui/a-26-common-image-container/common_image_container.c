/* EvenHub common image container, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenHub\common_image_container.c (log tag
 * "common_image_container"). Native 0x4dbeac..0x4dccd6: static pad-all helper 0x4dbeac,
 * common_image_create 0x4dbede, common_image_set_data 0x4dc5ae, common_image_destroy 0x4dca3c,
 * gray color helper 0x4dcc80 (not in the function inventory) and CRC16 0x4dcc98; literal pools
 * 0x4dca18..0x4dca3c and 0x4dcba8..0x4dcc80.
 *
 * An image container is a transparent LVGL object holding one lv_image backed by an L8
 * (8-bit gray) buffer of width x height bytes. EvenHub image fragments are reassembled into
 * rev_buf by the data parser (evenhub_data_parser.c); set_data converts a 4-bit palette BMP
 * into the L8 buffer and points the lv_image at it. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define IMAGE_MAX_X 0x240
#define IMAGE_MAX_Y 0x120
#define IMAGE_MIN_SIZE 20u
#define IMAGE_MAX_WIDTH 0x120u           /* 288 */
#define IMAGE_MAX_HEIGHT 0x90u           /* 144 */
#define IMAGE_MAX_BORDER_WIDTH 5u
#define IMAGE_MAX_RADIUS 0x20u
#define IMAGE_MAX_GRAY 0xffu

#define BMP_SIGNATURE 0x4d42u            /* "BM" */
#define BMP_HEADER_SIZE 0x36u
#define BMP_BIT_DEPTH 4u
#define BMP_PALETTE_DEFAULT 16u

#define LV_IMAGE_HEADER_MAGIC 0x19u
#define LV_COLOR_FORMAT_L8 0x06u

/* Creation config (shared layout with evenhub_image_config_t in evenhub_ui_private.h). */
typedef struct {
    int16_t x;                           /* +0x00 */
    int16_t y;                           /* +0x02 */
    uint16_t width;                      /* +0x04 */
    uint16_t height;                     /* +0x06 */
    uint8_t border_width;                /* +0x08 */
    uint8_t reserved_09[3];
    uint32_t border_color;               /* +0x0c gray level */
    uint8_t border_radius;               /* +0x10 */
    uint8_t reserved_11[3];
    uint32_t bg_color;                   /* +0x14 gray level */
    uint8_t reserved_18[4];
} common_image_config_t;
_Static_assert(sizeof(common_image_config_t) == 0x1c, "image config");

/* LVGL 9 lv_image_header_t / lv_image_dsc_t. */
typedef struct {
    uint32_t magic : 8;
    uint32_t cf : 8;
    uint32_t flags : 16;
    uint32_t w : 16;
    uint32_t h : 16;
    uint32_t stride : 16;
    uint32_t reserved_2 : 16;
} image_header_t;

typedef struct {
    image_header_t header;               /* +0x00 */
    uint32_t data_size;                  /* +0x0c */
    const uint8_t *data;                 /* +0x10 */
    const void *reserved;                /* +0x14 */
    const void *reserved_2;              /* +0x18 */
} image_dsc_t;
_Static_assert(sizeof(image_dsc_t) == 0x1c, "lv_image_dsc_t");

typedef struct {
    void *obj;                           /* +0x00 container lv_obj */
    void *image;                         /* +0x04 lv_image */
    uint8_t *image_buf;                  /* +0x08 L8 pixels shown by the image */
    uint8_t *rev_buf;                    /* +0x0c raw data receive buffer (data parser) */
    uint32_t session_id;                 /* +0x10 data parser reassembly state */
    uint32_t total_size;                 /* +0x14 */
    uint32_t compress_mode;              /* +0x18 */
    uint32_t fragment_index;             /* +0x1c */
    uint32_t received;                   /* +0x20 */
    image_dsc_t dsc;                     /* +0x24 */
    uint16_t width;                      /* +0x40 */
    uint16_t height;                     /* +0x42 */
    uint32_t buf_size;                   /* +0x44 width * height */
} common_image_handle_t;
_Static_assert(offsetof(common_image_handle_t, dsc) == 0x24, "image handle");
_Static_assert(sizeof(common_image_handle_t) == 0x48, "image handle");

/* Windows BMP file + info header, 4-bit palette layout. */
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
    uint32_t colors_used;                /* +0x2e 0 = 16 */
    uint32_t colors_important;           /* +0x32 */
    uint8_t palette[1][4];               /* +0x36 {blue, green, red, 0} */
} bmp_header_t;
_Static_assert(offsetof(bmp_header_t, palette) == BMP_HEADER_SIZE, "bmp header");

/* LVGL (stock copies). lv_color_t {blue, green, red} travels in r0. */
extern void *audio_uart_page_43de82(void *parent);                           /* lv_obj_create */
extern void audio_uart_page_43f09a(void *obj, int32_t x, int32_t y);         /* lv_obj_set_pos */
extern void audio_uart_page_43f4c0(void *obj, int32_t w, int32_t h);         /* lv_obj_set_size */
extern uint32_t audio_uart_page_441068(uint32_t r, uint32_t g, uint32_t b);  /* lv_color_make */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel);      /* pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel);      /* pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel);      /* pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel);      /* pad_right */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t sel); /* bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t opa, uint32_t sel);   /* bg_opa */
extern void audio_uart_page_4412ec(void *obj, uint32_t color, uint32_t sel); /* border_color */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t sel);      /* border_width */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);      /* radius */
extern void *audio_uart_page_498668(void *parent);                           /* lv_image_create */
extern void audio_uart_page_498680(void *image, const void *src);            /* lv_image_set_src */
extern void audio_uart_page_invalidate_440656(void *obj);                    /* lv_obj_invalidate */
extern void audio_uart_page_delete_event_filter_44d7b8(void *obj);           /* lv_obj_delete */
/* (green * 36 + red * 220) >> 8 of an lv_color_t. */
extern uint8_t color_to_gray_5456d6(uint32_t color);

/* System. */
extern void *file_heap_allocate(uint32_t size); /* 0x474cd2 */
extern void file_heap_free(void *buffer);       /* 0x474d16 */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* memset 0x43c0e4 */
extern uint32_t audio_uart_cache_clean_range_47510e(const uint32_t *range); /* {addr, size} */
extern int32_t iar_abs_509694(int32_t v);

/* Logging. */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char img_tag[] = "common_image_container"; /* ROM 0x775a04 */
static const char img_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenHub\\common_image_container.c"; /* ROM 0x6eba88 */
static const char fn_create[] = "common_image_create";    /* ROM 0x77e8fc */
static const char fn_set_data[] = "common_image_set_data"; /* ROM 0x775a1c */
static const char fn_destroy[] = "common_image_destroy";   /* ROM 0x775a34 */

static const char s_bad_args[] = "Invalid parameters: parent=%p, config=%p"; /* ROM 0x73c928 */
static const char s_bad_args_s[] =
    "[common_image_container]Invalid parameters: parent=%p, config=%p"; /* ROM 0x700afc */
static const char s_w_small[] = "common_image_create: width %d < 20, clamping to 20"; /* ROM 0x7275a8 */
static const char s_w_small_s[] =
    "[common_image_container]common_image_create: width %d < 20, clamping to 20"; /* ROM 0x6f1df0 */
static const char s_w_big[] = "common_image_create: width %d > %d, clamping to %d"; /* ROM 0x7275dc */
static const char s_w_big_s[] =
    "[common_image_container]common_image_create: width %d > %d, clamping to %d"; /* ROM 0x6f1e3c */
static const char s_h_small[] = "common_image_create: height %d < 20, clamping to 20"; /* ROM 0x727610 */
static const char s_h_small_s[] =
    "[common_image_container]common_image_create: height %d < 20, clamping to 20"; /* ROM 0x6f1e88 */
static const char s_h_big[] = "common_image_create: height %d > %d, clamping to %d"; /* ROM 0x727644 */
static const char s_h_big_s[] =
    "[common_image_container]common_image_create: height %d > %d, clamping to %d"; /* ROM 0x6f1ed4 */
static const char s_creating[] =
    "Creating image container: pos(%d,%d) size(%dx%d) border(%d,%d,%d) bg(%d)"; /* ROM 0x6f1f20 */
static const char s_creating_s[] = "[common_image_container]Creating image container: pos(%d,%d) "
                                   "size(%dx%d) border(%d,%d,%d) bg(%d)"; /* ROM 0x6da228 */
static const char s_no_handle[] = "Failed to allocate handle memory"; /* ROM 0x752838 */
static const char s_no_handle_s[] =
    "[common_image_container]Failed to allocate handle memory"; /* ROM 0x712b68 */
static const char s_no_buf[] = "Failed to allocate image buffer (%d bytes)"; /* ROM 0x73c954 */
static const char s_no_buf_s[] =
    "[common_image_container]Failed to allocate image buffer (%d bytes)"; /* ROM 0x700b40 */
static const char s_no_rev[] = "Failed to allocate rev buffer (%d bytes)"; /* ROM 0x73c980 */
static const char s_no_rev_s[] =
    "[common_image_container]Failed to allocate rev buffer (%d bytes)"; /* ROM 0x700b84 */
static const char s_unaligned[] = "Image buffer not 4-byte aligned: %p"; /* ROM 0x75285c */
static const char s_unaligned_s[] =
    "[common_image_container]Image buffer not 4-byte aligned: %p"; /* ROM 0x712ba4 */
static const char s_buf_ok[] = "Image buffer allocated: %p, size=%d bytes"; /* ROM 0x73c9ac */
static const char s_buf_ok_s[] =
    "[common_image_container]Image buffer allocated: %p, size=%d bytes"; /* ROM 0x700bc8 */
static const char s_no_obj[] = "Failed to create container object"; /* ROM 0x752880 */
static const char s_no_obj_s[] =
    "[common_image_container]Failed to create container object"; /* ROM 0x712be0 */
static const char s_no_image[] = "Failed to create image object"; /* ROM 0x75e6b0 */
static const char s_no_image_s[] = "[common_image_container]Failed to create image object"; /* ROM 0x71c818 */
static const char s_created[] = "Image container created successfully: handle=%p"; /* ROM 0x731f34 */
static const char s_created_s[] =
    "[common_image_container]Image container created successfully: handle=%p"; /* ROM 0x6f8b4c */

static const char s_sd_args[] = "Invalid parameters: handle=%p, data=%p"; /* ROM 0x74837c */
static const char s_sd_args_s[] =
    "[common_image_container]Invalid parameters: handle=%p, data=%p"; /* ROM 0x709aa4 */
static const char s_short[] = "Data too short: %d bytes"; /* ROM 0x76a0c4 */
static const char s_short_s[] = "[common_image_container]Data too short: %d bytes"; /* ROM 0x727678 */
static const char s_sig[] = "Invalid BMP signature: 0x%04X (expected 0x%04X)"; /* ROM 0x731f64 */
static const char s_sig_s[] =
    "[common_image_container]Invalid BMP signature: 0x%04X (expected 0x%04X)"; /* ROM 0x6f8b94 */
static const char s_depth[] = "BMP bit depth mismatch: expected %d-bit, got %d-bit"; /* ROM 0x7276ac */
static const char s_depth_s[] =
    "[common_image_container]BMP bit depth mismatch: expected %d-bit, got %d-bit"; /* ROM 0x6f1f6c */
static const char s_size[] = "BMP size mismatch: expected %dx%d, got %dx%d"; /* ROM 0x731f94 */
static const char s_size_s[] =
    "[common_image_container]BMP size mismatch: expected %dx%d, got %dx%d"; /* ROM 0x6f8bdc */
static const char s_proc[] = "Processing 4bit BMP data: %dx%d"; /* ROM 0x75e6d0 */
static const char s_proc_s[] = "[common_image_container]Processing 4bit BMP data: %dx%d"; /* ROM 0x71c850 */
static const char s_conv[] = "Image data converted: %dx%d, CRC16=0x%04X, size=%d bytes"; /* ROM 0x712c1c */
static const char s_conv_s[] =
    "[common_image_container]Image data converted: %dx%d, CRC16=0x%04X, size=%d bytes"; /* ROM 0x6e6814 */
static const char s_cache[] = "D-Cache cleaned for image buffer: addr=0x%08X, size=%d"; /* ROM 0x71c888 */
static const char s_cache_s[] =
    "[common_image_container]D-Cache cleaned for image buffer: addr=0x%08X, size=%d"; /* ROM 0x6ebad8 */
static const char s_updated[] = "Image data updated successfully"; /* ROM 0x75e6f0 */
static const char s_updated_s[] = "[common_image_container]Image data updated successfully"; /* ROM 0x71c8c0 */

static const char s_null[] = "Destroy called with NULL handle"; /* ROM 0x75e710 */
static const char s_null_s[] = "[common_image_container]Destroy called with NULL handle"; /* ROM 0x71c8f8 */
static const char s_destroying[] = "Destroying image container: handle=%p"; /* ROM 0x7483a4 */
static const char s_destroying_s[] =
    "[common_image_container]Destroying image container: handle=%p"; /* ROM 0x709ae4 */
static const char s_rev_freed[] = "Rev buffer freed"; /* ROM 0x77e910 */
static const char s_rev_freed_s[] = "[common_image_container]Rev buffer freed"; /* ROM 0x73c9d8 */
static const char s_buf_freed[] = "Image buffer freed"; /* ROM 0x77e924 */
static const char s_buf_freed_s[] = "[common_image_container]Image buffer freed"; /* ROM 0x73ca04 */
static const char s_destroyed[] = "Image container destroyed"; /* ROM 0x76a0e0 */
static const char s_destroyed_s[] = "[common_image_container]Image container destroyed"; /* ROM 0x7276e0 */

/* Both sinks are tested separately and the arguments are evaluated per sink, as in stock. */
#define IMG_LOG(level, func, line, cflags, text, short_text, ...)                             \
    do {                                                                                      \
        if ((audio_log_flags() & 2u) != 0u)                                                   \
            audio_log_extended((level), img_tag, img_file, (func), (line), (text),            \
                               ##__VA_ARGS__);                                                \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                 \
            (void)compress_log_output((cflags), (short_text), (short_text), ##__VA_ARGS__);   \
    } while (0)

uint16_t image_crc16_modbus_4dcc98(const uint8_t *data, uint32_t len);
uint32_t image_gray_color_4dcc80(uint8_t level);

/* lv_obj_set_style_pad_all (file-local copy; same body as 0x4935cc / 0x4dccd8). */
void image_obj_set_style_pad_all_4dbeac(void *obj, int32_t value, uint32_t selector)
{
    audio_uart_page_44122a(obj, value, selector);
    audio_uart_page_441238(obj, value, selector);
    audio_uart_page_44120e(obj, value, selector);
    audio_uart_page_44121c(obj, value, selector);
}

/* Point dsc at the L8 image buffer (done after create and after every data update). */
static void image_dsc_fill(common_image_handle_t *h)
{
    h->dsc.header.magic = LV_IMAGE_HEADER_MAGIC;
    h->dsc.header.cf = LV_COLOR_FORMAT_L8;
    h->dsc.header.flags = 0u;
    h->dsc.header.stride = h->width;
    h->dsc.header.w = h->width;
    h->dsc.header.h = h->height;
    h->dsc.data_size = h->buf_size;
    h->dsc.data = h->image_buf;
    h->dsc.reserved = NULL;
    h->dsc.reserved_2 = NULL;
}

/* Returns NULL when an argument is NULL or the size is out of range (the "clamping" log
 * messages notwithstanding, out-of-range sizes are rejected). */
common_image_handle_t *common_image_container_create_4dbede(void *parent,
                                                            const common_image_config_t *config)
{
    common_image_config_t cfg;
    common_image_handle_t *h;

    if (parent == NULL || config == NULL) {
        IMG_LOG(1, fn_create, 0x34, 0x4800000u, s_bad_args, s_bad_args_s, parent, config);
        return NULL;
    }
    cfg = *config;
    if (cfg.x > IMAGE_MAX_X)
        cfg.x = IMAGE_MAX_X;
    if (cfg.y > IMAGE_MAX_Y)
        cfg.y = IMAGE_MAX_Y;
    if (cfg.width < IMAGE_MIN_SIZE) {
        IMG_LOG(2, fn_create, 0x41, 0x8400000u, s_w_small, s_w_small_s, (uint32_t)cfg.width);
        return NULL;
    }
    if (cfg.width > IMAGE_MAX_WIDTH) {
        IMG_LOG(2, fn_create, 0x46, 0x8c00000u, s_w_big, s_w_big_s, (uint32_t)cfg.width,
                IMAGE_MAX_WIDTH, IMAGE_MAX_WIDTH);
        return NULL;
    }
    if (cfg.height < IMAGE_MIN_SIZE) {
        IMG_LOG(2, fn_create, 0x4a, 0x8400000u, s_h_small, s_h_small_s, (uint32_t)cfg.height);
        return NULL;
    }
    if (cfg.height > IMAGE_MAX_HEIGHT) {
        IMG_LOG(2, fn_create, 0x4e, 0x8c00000u, s_h_big, s_h_big_s, (uint32_t)cfg.height,
                IMAGE_MAX_HEIGHT, IMAGE_MAX_HEIGHT);
        return NULL;
    }
    if (cfg.border_width > IMAGE_MAX_BORDER_WIDTH)
        cfg.border_width = IMAGE_MAX_BORDER_WIDTH;
    if (cfg.border_color > IMAGE_MAX_GRAY)
        cfg.border_color = IMAGE_MAX_GRAY;
    if (cfg.border_radius > IMAGE_MAX_RADIUS)
        cfg.border_radius = IMAGE_MAX_RADIUS;
    if (cfg.bg_color > IMAGE_MAX_GRAY)
        cfg.bg_color = IMAGE_MAX_GRAY;
    IMG_LOG(4, fn_create, 0x62, 0x12000000u, s_creating, s_creating_s, (int32_t)cfg.x,
            (int32_t)cfg.y, (uint32_t)cfg.width, (uint32_t)cfg.height, (uint32_t)cfg.border_width,
            cfg.border_color, (uint32_t)cfg.border_radius, cfg.bg_color);

    h = (common_image_handle_t *)file_heap_allocate(sizeof(*h));
    if (h == NULL) {
        IMG_LOG(1, fn_create, 0x67, 0x4000000u, s_no_handle, s_no_handle_s);
        return NULL;
    }
    audio_uart_buffer_zero(h, sizeof(*h), 0u);
    h->width = cfg.width;
    h->height = cfg.height;
    h->buf_size = (uint32_t)cfg.height * cfg.width;

    h->image_buf = (uint8_t *)file_heap_allocate(h->buf_size);
    if (h->image_buf == NULL) {
        IMG_LOG(1, fn_create, 0x74, 0x4400000u, s_no_buf, s_no_buf_s, h->buf_size);
        file_heap_free(h);
        return NULL;
    }
    audio_uart_buffer_zero(h->image_buf, h->buf_size, 0u);

    h->rev_buf = (uint8_t *)file_heap_allocate(h->buf_size);
    if (h->rev_buf == NULL) {
        IMG_LOG(1, fn_create, 0x7d, 0x4400000u, s_no_rev, s_no_rev_s, h->buf_size);
        file_heap_free(h->image_buf);
        file_heap_free(h);
        return NULL;
    }
    audio_uart_buffer_zero(h->rev_buf, h->buf_size, 0u);

    if (((uintptr_t)h->image_buf & 3u) != 0u)
        IMG_LOG(2, fn_create, 0x86, 0x8400000u, s_unaligned, s_unaligned_s, h->image_buf);
    IMG_LOG(4, fn_create, 0x8a, 0x10800000u, s_buf_ok, s_buf_ok_s, h->image_buf, h->buf_size);

    h->obj = audio_uart_page_43de82(parent);
    if (h->obj == NULL) {
        IMG_LOG(1, fn_create, 0x8f, 0x4000000u, s_no_obj, s_no_obj_s);
        file_heap_free(h->rev_buf);
        file_heap_free(h->image_buf);
        file_heap_free(h);
        return NULL;
    }
    audio_uart_page_43f09a(h->obj, cfg.x, cfg.y);
    audio_uart_page_43f4c0(h->obj, cfg.width, cfg.height);
    audio_uart_page_44127e(h->obj, image_gray_color_4dcc80((uint8_t)cfg.bg_color), 0u);
    audio_uart_page_44129e(h->obj, 0u, 0u); /* LV_OPA_TRANSP */
    audio_uart_page_44131c(h->obj, cfg.border_width, 0u);
    if (cfg.border_width != 0u)
        audio_uart_page_4412ec(h->obj, image_gray_color_4dcc80((uint8_t)cfg.border_color), 0u);
    audio_uart_page_44146a(h->obj, cfg.border_radius, 0u);
    image_obj_set_style_pad_all_4dbeac(h->obj, 0, 0u);
    image_dsc_fill(h);

    h->image = audio_uart_page_498668(h->obj);
    if (h->image == NULL) {
        IMG_LOG(1, fn_create, 0xbf, 0x4000000u, s_no_image, s_no_image_s);
        audio_uart_page_delete_event_filter_44d7b8(h->obj);
        file_heap_free(h->rev_buf);
        file_heap_free(h->image_buf);
        file_heap_free(h);
        return NULL;
    }
    IMG_LOG(4, fn_create, 0xcd, 0x10400000u, s_created, s_created_s, h);
    return h;
}

/* Convert a 4-bit palette BMP of exactly the container size into the L8 buffer
 * (palette entry -> lv_color -> gray) and show it. Returns 0 or -1. */
int32_t common_image_container_set_data_4dc5ae(common_image_handle_t *h, const uint8_t *data,
                                               uint32_t len)
{
    const bmp_header_t *bmp = (const bmp_header_t *)data;
    const uint8_t *pixels;
    uint8_t *dst;
    uint32_t width;
    uint32_t height;
    uint32_t colors;
    int32_t stride;
    int32_t y;
    int32_t x;
    uint16_t crc;
    uint32_t range[2];

    if (h == NULL || data == NULL) {
        IMG_LOG(1, fn_set_data, 0xdb, 0x4800000u, s_sd_args, s_sd_args_s, h, data);
        return -1;
    }
    if (len < BMP_HEADER_SIZE) {
        IMG_LOG(1, fn_set_data, 0xe0, 0x4400000u, s_short, s_short_s, len);
        return -1;
    }
    if (bmp->signature != BMP_SIGNATURE) {
        IMG_LOG(1, fn_set_data, 0xe8, 0x4800000u, s_sig, s_sig_s, (uint32_t)bmp->signature,
                BMP_SIGNATURE);
        return -1;
    }
    if (bmp->bit_count != BMP_BIT_DEPTH) {
        IMG_LOG(1, fn_set_data, 0xf3, 0x4800000u, s_depth, s_depth_s, BMP_BIT_DEPTH,
                (uint32_t)bmp->bit_count);
        return -1;
    }
    width = (uint32_t)bmp->width;
    height = (uint32_t)iar_abs_509694(bmp->height);
    if (width != h->width || height != h->height) {
        IMG_LOG(1, fn_set_data, 0xfc, 0x5000000u, s_size, s_size_s, (uint32_t)h->width,
                (uint32_t)h->height, width, height);
        return -1;
    }
    IMG_LOG(4, fn_set_data, 0x100, 0x10800000u, s_proc, s_proc_s, width, height);

    colors = (bmp->colors_used == 0u) ? BMP_PALETTE_DEFAULT : bmp->colors_used;
    pixels = data + bmp->data_offset;
    stride = (((int32_t)(width + 1u) / 2) + 3) / 4 * 4;
    dst = h->image_buf;
    for (y = 0; y < (int32_t)height; y++) {
        for (x = 0; x < (int32_t)width; x++) {
            int32_t row = y;
            uint8_t byte;
            uint32_t index;

            if (bmp->height > 0)
                row = (int32_t)(height - 1u) - y;
            byte = pixels[stride * row + x / 2];
            index = ((x & 1) != 0) ? (uint32_t)(byte & 0xfu) : (uint32_t)(byte >> 4);
            if (index >= colors)
                index = 0u;
            dst[width * (uint32_t)y + (uint32_t)x] = color_to_gray_5456d6(audio_uart_page_441068(
                bmp->palette[index][2], bmp->palette[index][1], bmp->palette[index][0]));
        }
    }

    crc = image_crc16_modbus_4dcc98(dst, h->buf_size);
    IMG_LOG(4, fn_set_data, 0x138, 0x11000000u, s_conv, s_conv_s, width, height, (uint32_t)crc,
            h->buf_size);
    range[0] = (uint32_t)(uintptr_t)h->image_buf;
    range[1] = h->buf_size;
    (void)audio_uart_cache_clean_range_47510e(range);
    IMG_LOG(4, fn_set_data, 0x140, 0x10800000u, s_cache, s_cache_s, range[0], range[1]);

    image_dsc_fill(h);
    audio_uart_page_498680(h->image, &h->dsc);
    audio_uart_page_invalidate_440656(h->image);
    IMG_LOG(4, fn_set_data, 0x154, 0x10000000u, s_updated, s_updated_s);
    return 0;
}

void common_image_destroy_4dca3c(common_image_handle_t *h)
{
    if (h == NULL) {
        IMG_LOG(2, fn_destroy, 0x15e, 0x8000000u, s_null, s_null_s);
        return;
    }
    IMG_LOG(4, fn_destroy, 0x162, 0x10400000u, s_destroying, s_destroying_s, h);
    if (h->obj != NULL) {
        audio_uart_page_delete_event_filter_44d7b8(h->obj); /* also deletes the child image */
        h->obj = NULL;
        h->image = NULL;
    }
    if (h->rev_buf != NULL) {
        file_heap_free(h->rev_buf);
        h->rev_buf = NULL;
        IMG_LOG(4, fn_destroy, 0x16f, 0x10000000u, s_rev_freed, s_rev_freed_s);
    }
    if (h->image_buf != NULL) {
        file_heap_free(h->image_buf);
        h->image_buf = NULL;
        IMG_LOG(4, fn_destroy, 0x176, 0x10000000u, s_buf_freed, s_buf_freed_s);
    }
    file_heap_free(h);
    IMG_LOG(4, fn_destroy, 0x17b, 0x10000000u, s_destroyed, s_destroyed_s);
}

/* lv_color_make(level, level, level). Missing from the function inventory (0x4dcc80..0x4dcc98). */
uint32_t image_gray_color_4dcc80(uint8_t level)
{
    return audio_uart_page_441068(level, level, level);
}

/* CRC-16/MODBUS (init 0xffff, reflected poly 0xa001), logged after BMP conversion. */
uint16_t image_crc16_modbus_4dcc98(const uint8_t *data, uint32_t len)
{
    uint16_t crc = 0xffffu;
    uint32_t i;
    int32_t bit;

    for (i = 0u; i < len; i++) {
        crc ^= data[i];
        for (bit = 0; bit < 8; bit++) {
            if ((crc & 1u) != 0u)
                crc = (uint16_t)((crc >> 1) ^ 0xa001u);
            else
                crc = (uint16_t)(crc >> 1);
        }
    }
    return crc;
}
