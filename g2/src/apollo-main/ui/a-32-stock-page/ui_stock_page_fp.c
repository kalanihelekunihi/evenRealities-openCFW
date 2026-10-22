/* Dashboard stock widget page (FP part), stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\screens\ui_stock_page.c.
 * Native 0x4ec2dc..0x4ece47 (StockWidget_MainPage_init) and 0x4ece5c..0x4ecfad
 * (price / percent formatting); literal pools 0x4ecd4c..0x4ecdaf,
 * 0x4ece48..0x4ece5b, 0x4ecec0..0x4ecec3, 0x4ecee4..0x4ecee7,
 * 0x4ecfb0..0x4ecfc7, 0x4ed048..0x4ed057, 0x4ed0f4..0x4ed12b, 0x4ed36c..0x4ed37b
 * and 0x4ed6e0..0x4ed71c.
 *
 * The formatters take doubles in d0/d1 (hard-float), and the page builder
 * widens the record floats with vcvt.f64.f32, so this unit needs the
 * double-precision profile g2-apollo-main-20. */
#include <stdint.h>
#include <stddef.h>

#include "ui_stock_page_private.h"

/* Non-expanded page geometry (container frame inside the 352x288 tile). */
#define FRAME_X 20
#define FRAME_Y 17
#define FRAME_W 315
#define FRAME_H 254
#define ROW_PITCH 96        /* one stock = two text rows */
#define SEPARATOR_W 312
#define SEPARATOR_Y1 79
#define SEPARATOR_Y2 175
#define NO_DATA_ICON 24     /* icon edge */
#define NO_DATA_ICON_GAP 8  /* icon -> first line */
#define NO_DATA_LINE_GAP 4  /* first line -> second line */
#define FORMAT_BUFFER 32u

/* Trend / no-data images (lv_image_dsc_t in ROM). */
extern const uint8_t g2_stock_no_data_img_772570[];   /* ROM 0x772570 */
extern const uint8_t g2_stock_trend1_img_7725c4[];    /* ROM 0x7725c4, changing_trend == 1 */
extern const uint8_t g2_stock_trend2_img_7725a8[];    /* ROM 0x7725a8, changing_trend == 2 */
extern const uint8_t g2_stock_trend_other_img_77258c[]; /* ROM 0x77258c */

typedef struct {
    int32_t x; /* +0 */
    int32_t y; /* +4 */
} g2_lv_point_t;

static const char stock_module_tag[] = "dashboard.stock"; /* ROM 0x789e80 */
static const char stock_source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\screens\\ui_stock_page.c"; /* ROM 0x6f0e98 */

static const char fn_init[] = "StockWidget_MainPage_init"; /* ROM 0x7743d8 */
static const char init_bad_index[] = "Invalid index %d, must be 0-5"; /* ROM 0x767d70 */
static const char init_bad_index_short[] = "[dashboard.stock]Invalid index %d, must be 0-5"; /* ROM 0x73b0b4 */
static const char init_no_tile[] = "tile_list[%d][1] is NULL"; /* ROM 0x7743f4 */
static const char init_no_tile_short[] = "[dashboard.stock]tile_list[%d][1] is NULL"; /* ROM 0x74671c */
static const char init_no_frame[] = "stock Failed to create container frame"; /* ROM 0x750f04 */
static const char init_no_frame_short[] = "[dashboard.stock]stock Failed to create container frame"; /* ROM 0x725e28 */
static const char init_clamp[] =
    "Widget: Container index %d exceeds max valid index %d (stock count: %d), adjusting to %d"; /* ROM 0x6e1f54 */
static const char init_clamp_short[] =
    "[dashboard.stock]Widget: Container index %d exceeds max valid index %d (stock count: %d), adjusting to %d"; /* ROM 0x6d8098 */
static const char init_reset[] = "Widget: No stock data, resetting container index from %d to 0"; /* ROM 0x711764 */
static const char init_reset_short[] =
    "[dashboard.stock]Widget: No stock data, resetting container index from %d to 0"; /* ROM 0x6f0f38 */
static const char init_line1[] = "Container %d separator_line1 shown (stocks: %d)"; /* ROM 0x73b0e4 */
static const char init_line1_short[] =
    "[dashboard.stock]Container %d separator_line1 shown (stocks: %d)"; /* ROM 0x708284 */
static const char init_line2[] = "Container %d separator_line2 shown (stocks: %d)"; /* ROM 0x73b114 */
static const char init_line2_short[] =
    "[dashboard.stock]Container %d separator_line2 shown (stocks: %d)"; /* ROM 0x7082c8 */
static const char init_done[] =
    "Non-expanded page created successfully for container %d with conditional separator lines (%d stocks) and click event"; /* ROM 0x6d6a88 */
static const char init_done_short[] =
    "[dashboard.stock]Non-expanded page created successfully for container %d with conditional separator lines (%d stocks) and click event"; /* ROM 0x6d4a10 */
static const char no_data_key1[] = "ID_DASHBOARD_STOCKS_DEFAULT_1"; /* ROM 0x767cd0 */
static const char no_data_key2[] = "ID_DASHBOARD_STOCKS_DEFAULT_2"; /* ROM 0x767cf0 */

static const char fn_buffer_valid[] = "is_stock_format_buffer_valid"; /* ROM 0x767d90 */
static const char buffer_invalid[] = "Invalid parameters - buffer=%p, buffer_size=%zu"; /* ROM 0x73b144 */
static const char buffer_invalid_short[] =
    "[dashboard.stock]Invalid parameters - buffer=%p, buffer_size=%zu"; /* ROM 0x70830c */
static const char placeholder[] = "-";           /* ROM 0x4ed128 */
static const char fmt_price[] = "%.2f";          /* ROM 0x78edac */
static const char fmt_gain[] = "+%.2f%%";        /* ROM 0x78edb4 */
static const char fmt_change[] = "%.2f%%";       /* ROM 0x78edbc */

int32_t is_stock_format_buffer_valid_4ece5c(char *buffer, size_t buffer_size)
{
    if (buffer == NULL || buffer_size == 0u) {
        STOCK_LOG(1u, 0x04800000u, 0x6adu, fn_buffer_valid, buffer_invalid, (void *)buffer, buffer_size);
        return 0;
    }
    return 1;
}

/* Returns sizeof("-"). */
int32_t stock_format_placeholder_4ecec4(char *buffer, size_t buffer_size)
{
    (void)audio_settings_copy_text(buffer, placeholder, (uint32_t)buffer_size);
    buffer[buffer_size - 1u] = '\0';
    return (int32_t)sizeof placeholder;
}

/* A price of exactly 0 means "no quote" and prints "-". */
__attribute__((pcs("aapcs-vfp"))) int32_t stock_format_price_4ecee8(char *buffer, size_t buffer_size,
                                                                    double price)
{
    if (!is_stock_format_buffer_valid_4ece5c(buffer, buffer_size))
        return -1;
    if (price == 0.0)
        return stock_format_placeholder_4ecec4(buffer, buffer_size);
    return g2_audio_dump_snprintf(buffer, (uint32_t)buffer_size, fmt_price, price);
}

__attribute__((pcs("aapcs-vfp"))) int32_t stock_format_change_percent_4ecf3c(char *buffer, size_t buffer_size,
                                                                             double price, double change_percent)
{
    if (!is_stock_format_buffer_valid_4ece5c(buffer, buffer_size))
        return -1;
    if (price == 0.0)
        return stock_format_placeholder_4ecec4(buffer, buffer_size);
    if (change_percent > 0.0)
        return g2_audio_dump_snprintf(buffer, (uint32_t)buffer_size, fmt_gain, change_percent);
    return g2_audio_dump_snprintf(buffer, (uint32_t)buffer_size, fmt_change, change_percent);
}

/* Two rows per stock: [trend icon][code ......... price]
 *                     [company ............. change %]   (IAR inlined this
 * three times with separate 32-byte buffers). */
static void create_stock_rows(void *frame, const g2_stock_record_t *stock, int32_t y)
{
    char price_text[FORMAT_BUFFER];
    char change_text[FORMAT_BUFFER];
    const void *const font = audio_uart_ring_primary_head_cell;

    void *icon = audio_lv_image_create_498668(frame);
    audio_lv_object_position_43f09a(icon, 0, y + 3);
    audio_lv_object_flag_43ded4(icon, LV_OBJ_FLAG_ADV_HITTEST);
    audio_lv_object_clear_flag_43dfa4(icon, LV_OBJ_FLAG_SCROLLABLE);
    if (stock->changing_trend == 1)
        audio_lv_image_source_498680(icon, g2_stock_trend1_img_7725c4);
    else if (stock->changing_trend == 2)
        audio_lv_image_source_498680(icon, g2_stock_trend2_img_7725a8);
    else
        audio_lv_image_source_498680(icon, g2_stock_trend_other_img_77258c);

    void *label = audio_lv_label_create_499416(frame);
    audio_lv_object_size_call_43f4c0(label, 156, 30);
    audio_lv_object_position_43f09a(label, 32, y);
    audio_lv_style_font_44143e(label, font, 0u);
    audio_lv_style_color_44140e(label, audio_lv_color_44104c(STOCK_WHITE), 0u);
    audio_lv_label_mode_499678(label, LV_LABEL_LONG_DOT);
    audio_lv_label_text_49942e(label, stock->code);

    label = audio_lv_label_create_499416(frame);
    audio_lv_object_size_call_43f4c0(label, 126, 30);
    audio_lv_object_position_43f09a(label, 189, y);
    audio_uart_page_44145a(label, LV_TEXT_ALIGN_RIGHT, 0u);
    audio_lv_style_font_44143e(label, font, 0u);
    audio_lv_style_color_44140e(label, audio_lv_color_44104c(STOCK_WHITE), 0u);
    (void)stock_format_price_4ecee8(price_text, sizeof price_text, (double)stock->current_price);
    audio_lv_label_text_49942e(label, price_text);

    label = audio_lv_label_create_499416(frame);
    audio_lv_object_size_call_43f4c0(label, 194, 28);
    audio_lv_object_position_43f09a(label, 0, y + 34);
    audio_lv_style_font_44143e(label, font, 0u);
    audio_lv_style_color_44140e(label, audio_lv_color_44104c(STOCK_WHITE), 0u);
    audio_lv_label_mode_499678(label, LV_LABEL_LONG_DOT);
    audio_lv_label_text_49942e(label, stock->company);

    label = audio_lv_label_create_499416(frame);
    audio_lv_object_size_call_43f4c0(label, 80, 28);
    audio_lv_object_position_43f09a(label, 235, y + 34);
    audio_uart_page_44145a(label, LV_TEXT_ALIGN_RIGHT, 0u);
    audio_lv_style_font_44143e(label, font, 0u);
    audio_lv_style_color_44140e(label, audio_lv_color_44104c(STOCK_WHITE), 0u);
    (void)stock_format_change_percent_4ecf3c(change_text, sizeof change_text, (double)stock->current_price,
                                             (double)stock->change_percent);
    audio_lv_label_text_49942e(label, change_text);
}

static void *create_separator(void *frame, int32_t y)
{
    void *line = audio_uart_page_43de82(frame);
    audio_lv_object_size_call_43f4c0(line, SEPARATOR_W, 1);
    audio_lv_object_position_43f09a(line, 0, y);
    audio_uart_page_44127e(line, audio_lv_color_44104c(STOCK_GREY), 0u);
    audio_uart_page_44129e(line, LV_OPA_COVER, 0u);
    audio_uart_page_44131c(line, 0, 0u);
    stock_obj_set_style_pad_all_4e9dd4(line, 0, 0u);
    return line;
}

/* "No stocks" placeholder: [icon][DEFAULT_1] centred, DEFAULT_2 below it. */
static void create_no_data_view(void)
{
    g2_lv_point_t line1_size;
    g2_lv_point_t line2_size;
    const int32_t icon_gap = NO_DATA_ICON_GAP;

    const char *const line1 = audio_uart_page_45fffe(no_data_key1, audio_uart_page_460084(no_data_key1));
    const char *const line2 = audio_uart_page_45fffe(no_data_key2, audio_uart_page_460084(no_data_key2));
    audio_uart_text_measure_489546(&line1_size, line1, audio_uart_ring_primary_head_cell, 0, 0, LV_COORD_MAX, 0u);
    const int32_t line1_width = line1_size.x;
    const int32_t row_height = line1_size.y > NO_DATA_ICON ? line1_size.y : NO_DATA_ICON;
    audio_uart_text_measure_489546(&line2_size, line2, audio_uart_ring_primary_head_cell, 0, 0, FRAME_W, 0u);
    if (line2_size.x > FRAME_W)
        line2_size.x = FRAME_W;

    const int32_t top = (FRAME_H - (line2_size.y + row_height + NO_DATA_LINE_GAP)) / 2;
    const int32_t line2_y = row_height + top + NO_DATA_LINE_GAP;
    const int32_t icon_x = (FRAME_W - (line1_width + icon_gap + NO_DATA_ICON)) / 2;
    const int32_t line1_x = icon_x + NO_DATA_ICON + icon_gap;

    g2_stock_no_data_icon_20074e44 = audio_lv_image_create_498668(g2_stock_container_frame_20074e3c);
    audio_lv_object_size_call_43f4c0(g2_stock_no_data_icon_20074e44, NO_DATA_ICON, NO_DATA_ICON);
    audio_lv_object_position_43f09a(g2_stock_no_data_icon_20074e44, icon_x, (row_height - NO_DATA_ICON) / 2 + top);
    audio_lv_image_source_498680(g2_stock_no_data_icon_20074e44, g2_stock_no_data_img_772570);

    g2_stock_no_data_label1_20074e48 = audio_lv_label_create_499416(g2_stock_container_frame_20074e3c);
    audio_lv_object_size_call_43f4c0(g2_stock_no_data_label1_20074e48, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    audio_lv_object_position_43f09a(g2_stock_no_data_label1_20074e48, line1_x, (row_height - line1_size.y) / 2 + top);
    audio_uart_page_44145a(g2_stock_no_data_label1_20074e48, LV_TEXT_ALIGN_LEFT, 0u);
    audio_lv_style_font_44143e(g2_stock_no_data_label1_20074e48, audio_uart_ring_primary_head_cell, 0u);
    audio_lv_style_color_44140e(g2_stock_no_data_label1_20074e48, audio_lv_color_44104c(STOCK_WHITE), 0u);
    audio_lv_label_text_49942e(g2_stock_no_data_label1_20074e48, line1);

    g2_stock_no_data_label2_20074e4c = audio_lv_label_create_499416(g2_stock_container_frame_20074e3c);
    audio_lv_object_size_call_43f4c0(g2_stock_no_data_label2_20074e4c, line2_size.x, LV_SIZE_CONTENT);
    audio_lv_object_position_43f09a(g2_stock_no_data_label2_20074e4c, (FRAME_W - line2_size.x) / 2, line2_y);
    audio_uart_page_44145a(g2_stock_no_data_label2_20074e4c, LV_TEXT_ALIGN_CENTER, 0u);
    audio_lv_style_font_44143e(g2_stock_no_data_label2_20074e4c, audio_uart_ring_primary_head_cell, 0u);
    audio_lv_style_color_44140e(g2_stock_no_data_label2_20074e4c, audio_lv_color_44104c(STOCK_WHITE), 0u);
    audio_lv_label_text_49942e(g2_stock_no_data_label2_20074e4c, line2);
}

/* Builds the non-expanded stock widget (three stocks of the current
 * container, or the no-data placeholder) inside dashboard tile tile_index. */
int32_t StockWidget_MainPage_init_4ec2dc(uint32_t tile_index)
{
    g2_stock_widget_init_flag_20074e2c = 0u;
    g2_stock_tilelist_index_20004328 = tile_index;
    if (g2_stock_tilelist_index_20004328 >= STOCK_TILE_COUNT) {
        STOCK_LOG(1u, 0x04400000u, 0x539u, fn_init, init_bad_index, g2_stock_tilelist_index_20004328);
        return -1;
    }
    if (g2_dashboard_tiles[g2_stock_tilelist_index_20004328].frame == NULL) {
        STOCK_LOG(1u, 0x04400000u, 0x53fu, fn_init, init_no_tile, g2_stock_tilelist_index_20004328);
        return -1;
    }

    g2_stock_container_frame_20074e3c = audio_uart_page_43de82(g2_dashboard_tiles[g2_stock_tilelist_index_20004328].frame);
    if (g2_stock_container_frame_20074e3c == NULL) {
        STOCK_LOG(1u, 0x04000000u, 0x547u, fn_init, init_no_frame);
        return -1;
    }
    audio_lv_object_position_43f09a(g2_stock_container_frame_20074e3c, FRAME_X, FRAME_Y);
    audio_lv_object_size_call_43f4c0(g2_stock_container_frame_20074e3c, FRAME_W, FRAME_H);
    audio_uart_page_44129e(g2_stock_container_frame_20074e3c, 0u, 0u);
    audio_uart_page_44131c(g2_stock_container_frame_20074e3c, 0, 0u);
    stock_obj_set_style_pad_all_4e9dd4(g2_stock_container_frame_20074e3c, 0, 0u);
    audio_uart_page_44e368(g2_stock_container_frame_20074e3c, LV_SCROLLBAR_MODE_OFF);

    /* Keep the container index inside the current stock count. */
    if (stock_page_get_count_4e9fd6() != 0u) {
        const uint16_t max_index = (uint16_t)(((int32_t)stock_page_get_count_4e9fd6() - 1) / 3);
        if ((int32_t)max_index < stock_get_container_index_4ebf20()) {
            STOCK_LOG(2u, 0x09000000u, 0x55du, fn_init, init_clamp, stock_get_container_index_4ebf20(), max_index,
                      g2_stock_page_data_201308dc.stock_num, max_index);
            g2_stock_container_index_20074e38 = max_index;
        }
    } else if (stock_get_container_index_4ebf20() != 0) {
        STOCK_LOG(4u, 0x10400000u, 0x563u, fn_init, init_reset, stock_get_container_index_4ebf20());
        g2_stock_container_index_20074e38 = 0;
    }
    g2_stock_widget_init_flag_20074e2c = 1u;

    if (stock_page_get_count_4e9fd6() == 0u) {
        create_no_data_view();
        return 0;
    }

    const int32_t container = stock_get_container_index_4ebf20();
    const int32_t first = container * STOCKS_PER_CONTAINER;
    for (int32_t slot = 0; slot < STOCKS_PER_CONTAINER; slot++) {
        if (first + slot < (int32_t)stock_page_get_count_4e9fd6())
            create_stock_rows(g2_stock_container_frame_20074e3c, &g2_stock_page_data_201308dc.stock[first + slot],
                              slot * ROW_PITCH);
    }

    const int32_t count = calculate_stocks_in_container_4ecfc8(container);
    void *const line1 = create_separator(g2_stock_container_frame_20074e3c, SEPARATOR_Y1);
    void *const line2 = create_separator(g2_stock_container_frame_20074e3c, SEPARATOR_Y2);
    if (count < 2)
        audio_lv_object_flag_43ded4(line1, LV_OBJ_FLAG_HIDDEN);
    else
        STOCK_LOG(4u, 0x10800000u, 0x697u, fn_init, init_line1, container, count);
    if (count < 3)
        audio_lv_object_flag_43ded4(line2, LV_OBJ_FLAG_HIDDEN);
    else
        STOCK_LOG(4u, 0x10800000u, 0x69eu, fn_init, init_line2, container, count);
    STOCK_LOG(4u, 0x10800000u, 0x6a1u, fn_init, init_done, container, count);
    return 0;
}
