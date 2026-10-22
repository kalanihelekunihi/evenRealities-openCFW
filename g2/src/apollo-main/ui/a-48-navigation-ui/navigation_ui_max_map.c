/* Stock D:\01_workspace\s200_ap510b_iar_git\app\gui\navigation\navigation_ui.c (log tag
 * "navigation.ui"): IMU compass start/stop and the max map image. Native 0x5455e4..0x545caa
 * (StartIMUCompassFunc 0x5455e4, StopIMUCompassFunc 0x54566c, gray helper 0x5456d6,
 * navigation_create_max_map 0x5456f6, CRC16 0x545868, navigation_set_max_map_data 0x5458a2,
 * navigation_free_max_map_buffer 0x545c5a); inline strings "ON"/"OFF" 0x545cac/0x545cb0;
 * literal pools 0x545cb4..0x545d17 and 0x5464a4..0x5464b7, 0x546608..0x54661f,
 * 0x5467d8..0x5467df.
 *
 * The max map is a 576x188 L8 image whose pixels live in a static buffer (RAM 0x202a6670)
 * described by a static lv_image_dsc_t (RAM 0x20073aac). The phone sends a 4-bit palette
 * BMP; navigation_set_max_map_data converts each palette entry to gray. The inventory rows
 * 0x545644 and 0x545844 are not entries: they fall inside 0x5455e4 and 0x5456f6. */
#include "navigation_ui_private.h"

static const char s_start_fn[] = "StartIMUCompassFunc"; /* ROM 0x78137c */
static const char s_start_ok[] = "StartIMUComassFunc: success"; /* ROM 0x76e6e0 */
static const char s_start_ok_s[] = "[navigation.ui]StartIMUComassFunc: success"; /* ROM 0x740340 */
static const char s_stop_fn[] = "StopIMUCompassFunc"; /* ROM 0x781390 */
static const char s_stop_fail[] = "StopIMUComassFunc: HUB_Close failed"; /* ROM 0x756cd8 */
static const char s_stop_fail_s[] = "[navigation.ui]StopIMUComassFunc: HUB_Close failed"; /* ROM 0x72af24 */
static const char s_create_fn[] = "navigation_create_max_map"; /* ROM 0x76e6fc */
static const char s_bad_parent[] = "Invalid parent object"; /* ROM 0x7798ec */
static const char s_bad_parent_s[] = "[navigation.ui]Invalid parent object"; /* ROM 0x74b5a4 */
static const char s_no_image[] = "Failed to create image object"; /* ROM 0x762530 */
static const char s_no_image_s[] = "[navigation.ui]Failed to create image object"; /* ROM 0x7358f4 */
static const char s_created[] = "Max map widget created at (%d,%d)"; /* ROM 0x756cfc */
static const char s_created_s[] = "[navigation.ui]Max map widget created at (%d,%d)"; /* ROM 0x72af58 */
static const char s_set_fn[] = "navigation_set_max_map_data"; /* ROM 0x76e718 */
static const char s_bad_args[] = "Invalid parameters"; /* ROM 0x7813a4 */
static const char s_bad_args_s[] = "[navigation.ui]Invalid parameters"; /* ROM 0x756d20 */
static const char s_bad_sig[] = "Invalid BMP signature"; /* ROM 0x779904 */
static const char s_bad_sig_s[] = "[navigation.ui]Invalid BMP signature"; /* ROM 0x74b5cc */
static const char s_bad_depth[] = "BMP bit depth mismatch: expected 4-bit, got %d-bit"; /* ROM 0x72af8c */
static const char s_bad_depth_s[] =
    "[navigation.ui]BMP bit depth mismatch: expected 4-bit, got %d-bit"; /* ROM 0x703e84 */
static const char s_bad_size[] = "BMP size mismatch: expected %dx%d, got %dx%d"; /* ROM 0x735924 */
static const char s_bad_size_s[] = "[navigation.ui]BMP size mismatch: expected %dx%d, got %dx%d"; /* ROM 0x7165c4 */
static const char s_proc[] = "Processing 4bit BMP data: %dx%d"; /* ROM 0x762550 */
static const char s_proc_s[] = "[navigation.ui]Processing 4bit BMP data: %dx%d"; /* ROM 0x735954 */
static const char s_conv[] =
    "Max map data converted: %dx%d, CRC16=0x%04X, size=%d bytes, Cache=%s"; /* ROM 0x6fb72c */
static const char s_conv_s[] =
    "[navigation.ui]Max map data converted: %dx%d, CRC16=0x%04X, size=%d bytes, Cache=%s"; /* ROM 0x6e8c2c */
static const char s_updated[] = "Max map data updated successfully with static descriptor pool"; /* ROM 0x70cea4 */
static const char s_updated_s[] =
    "[navigation.ui]Max map data updated successfully with static descriptor pool"; /* ROM 0x6ee5f8 */
static const char s_free_fn[] = "navigation_free_max_map_buffer"; /* ROM 0x762570 */
static const char s_cleared[] = "simple_bmp_buffer cleared (static buffer)"; /* ROM 0x74036c */
static const char s_cleared_s[] = "[navigation.ui]simple_bmp_buffer cleared (static buffer)"; /* ROM 0x716600 */
static const char s_on[] = "ON";   /* inline 0x545cac */
static const char s_off[] = "OFF"; /* inline 0x545cb0 */

/* Compass parameters passed to HUB_ParameterConfig: 1000 ms period, 5. */
#define NAV_HUB_FUNC_COMPASS 2u

int32_t StartIMUCompassFunc_5455e4(void)
{
    int32_t param[2];

    g2_nav_compass_enabled_20074808 = 1u;
    g2_nav_compass_heading_2007480c = 0;
    if (HUB_Open(NAV_HUB_FUNC_COMPASS) != 0)
        return -1;
    param[0] = 1000;
    param[1] = 5;
    if (audio_hub_parameter_config_4a6e3c(NAV_HUB_FUNC_COMPASS, param) != 0u)
        return -1;
    NAV_LOG(3, s_start_fn, 0x10b, 0xc000000u, s_start_ok, s_start_ok_s);
    return 0;
}

int32_t StopIMUCompassFunc_54566c(void)
{
    g2_nav_compass_enabled_20074808 = 0u;
    g2_nav_compass_heading_2007480c = 0;
    if (HUB_Close(NAV_HUB_FUNC_COMPASS) != 0) {
        NAV_LOG(1, s_stop_fn, 0x114, 0x4000000u, s_stop_fail, s_stop_fail_s);
        return -1;
    }
    return 0;
}

/* (green * 36 + red * 220) >> 8 of an lv_color_t {blue, green, red} passed in r0. */
uint8_t color_to_gray_5456d6(uint32_t color)
{
    uint8_t green = (uint8_t)(color >> 8);
    uint8_t red = (uint8_t)(color >> 16);

    return (uint8_t)((uint16_t)(green * 0x24 + red * 0xdc) >> 8);
}

static void max_map_dsc_fill(void)
{
    nav_image_dsc_t *dsc = &g2_navigation_max_map_dsc_20073aac;

    dsc->header.magic = LV_IMAGE_HEADER_MAGIC;
    dsc->header.cf = LV_COLOR_FORMAT_L8;
    dsc->header.flags = 0u;
    dsc->header.stride = NAV_MAX_MAP_W;
    dsc->header.w = NAV_MAX_MAP_W;
    dsc->header.h = NAV_MAX_MAP_H;
    dsc->data_size = NAV_MAX_MAP_L8_SIZE;
    dsc->data = g2_navigation_max_map_buf_202a6670;
    dsc->reserved = NULL;
    dsc->reserved_2 = NULL;
}

void *navigation_create_max_map_5456f6(void *parent, int32_t x, int32_t y)
{
    void *img;

    if (parent == NULL) {
        NAV_LOG(1, s_create_fn, 0x12f, 0x4000000u, s_bad_parent, s_bad_parent_s);
        return NULL;
    }
    audio_uart_buffer_zero(g2_navigation_max_map_buf_202a6670, NAV_MAX_MAP_L8_SIZE, 0u);
    max_map_dsc_fill();
    img = audio_uart_page_498668(parent);
    if (img == NULL) {
        NAV_LOG(1, s_create_fn, 0x146, 0x4000000u, s_no_image, s_no_image_s);
        return NULL;
    }
    audio_uart_page_498680(img, &g2_navigation_max_map_dsc_20073aac);
    audio_uart_page_43f09a(img, x, y);
    NAV_LOG(4, s_create_fn, 0x150, 0x10800000u, s_created, s_created_s, x, y);
    return img;
}

/* CRC-16/CCITT-FALSE (poly 0x1021, init 0xffff, MSB first). */
uint16_t navigation_crc16_ccitt_545868(const uint8_t *data, uint32_t len)
{
    uint32_t crc = 0xffffu;
    uint32_t i;
    int32_t bit;

    for (i = 0u; i < len; i++) {
        crc ^= (uint32_t)data[i] << 8;
        for (bit = 0; bit < 8; bit++) {
            if ((crc & 0x8000u) != 0u)
                crc = (crc << 1) ^ 0x1021u;
            else
                crc <<= 1;
        }
    }
    return (uint16_t)crc;
}

int32_t navigation_set_max_map_data_5458a2(void *img, const uint8_t *bmp_data)
{
    const nav_bmp_header_t *bmp = (const nav_bmp_header_t *)bmp_data;
    const uint8_t *pixels;
    uint8_t *dst = g2_navigation_max_map_buf_202a6670;
    uint32_t width;
    uint32_t height;
    uint32_t colors;
    uint32_t cache;
    uint32_t range[2];
    uint16_t crc;
    int32_t y;
    int32_t x;

    if (img == NULL || bmp_data == NULL) {
        NAV_LOG(1, s_set_fn, 0x174, 0x4000000u, s_bad_args, s_bad_args_s);
        return -1;
    }
    if (bmp->signature != NAV_BMP_SIGNATURE) {
        NAV_LOG(1, s_set_fn, 0x17b, 0x4000000u, s_bad_sig, s_bad_sig_s);
        return -1;
    }
    if (bmp->bit_count != NAV_BMP_BIT_DEPTH) {
        NAV_LOG(1, s_set_fn, 0x183, 0x4400000u, s_bad_depth, s_bad_depth_s, (uint32_t)bmp->bit_count);
        return -1;
    }
    width = (uint32_t)bmp->width;
    height = (uint32_t)iar_abs_509694(bmp->height);
    if (width != NAV_MAX_MAP_W || height != NAV_MAX_MAP_H) {
        NAV_LOG(1, s_set_fn, 0x18c, 0x5000000u, s_bad_size, s_bad_size_s, NAV_MAX_MAP_W, NAV_MAX_MAP_H,
                width, height);
        return -1;
    }
    NAV_LOG(4, s_set_fn, 400, 0x10800000u, s_proc, s_proc_s, width, height);

    colors = (bmp->colors_used == 0u) ? NAV_BMP_PALETTE_DEFAULT : bmp->colors_used;
    pixels = bmp_data + bmp->data_offset;
    for (y = 0; y < (int32_t)NAV_MAX_MAP_H; y++) {
        for (x = 0; x < (int32_t)NAV_MAX_MAP_W; x++) {
            int32_t row = y;
            uint8_t byte;
            uint32_t index;

            if (bmp->height > 0)
                row = (int32_t)NAV_MAX_MAP_H - 1 - y;
            byte = pixels[NAV_BMP_ROW_STRIDE * (uint32_t)row + (uint32_t)(x / 2)];
            index = ((x & 1) != 0) ? (uint32_t)(byte & 0xfu) : (uint32_t)(byte >> 4);
            if (index >= colors)
                index = 0u;
            dst[NAV_MAX_MAP_W * (uint32_t)y + (uint32_t)x] = color_to_gray_5456d6(audio_uart_page_441068(
                bmp->palette[index][2], bmp->palette[index][1], bmp->palette[index][0]));
        }
    }

    crc = navigation_crc16_ccitt_545868(dst, NAV_MAX_MAP_L8_SIZE);
    cache = audio_uart_lv_image_cache_enabled_4d4b24() & 0xffu;
    NAV_LOG(4, s_set_fn, 0x1cc, 0x11400000u, s_conv, s_conv_s, width, height, (uint32_t)crc,
            NAV_MAX_MAP_L8_SIZE, (cache != 0u) ? s_on : s_off);
    range[0] = (uint32_t)(uintptr_t)dst;
    range[1] = NAV_MAX_MAP_L8_SIZE;
    (void)audio_uart_cache_clean_range_47510e(range);

    max_map_dsc_fill();
    audio_uart_page_498680(img, &g2_navigation_max_map_dsc_20073aac);
    audio_uart_page_invalidate_440656(img);
    NAV_LOG(4, s_set_fn, 0x1fc, 0x10000000u, s_updated, s_updated_s);
    return 0;
}

void navigation_free_max_map_buffer_545c5a(void)
{
    audio_uart_buffer_zero(g2_navigation_max_map_buf_202a6670, NAV_MAX_MAP_L8_SIZE, 0u);
    NAV_LOG(4, s_free_fn, 0x206, 0x10000000u, s_cleared, s_cleared_s);
}
