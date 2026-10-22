/* Dashboard stock widget page (non-FP part), stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\screens\ui_stock_page.c.
 * Native 0x4ebf20..0x4ebf25, 0x4ebf5c..0x4ec217, 0x4ecfc8..0x4ed0f3,
 * 0x4ed12c..0x4ed6df; literal pools 0x4ec218..0x4ec2db, 0x4ed6e0..0x4ed7d7
 * (shared with ui_stock_page_fp.c).
 *
 * Covers the page refresh entry (Stock_Page_Reflash), the per-container stock
 * count, separator-line visibility, the vertical page-dot indicator of the
 * expanded page and its cleanup / container-switch helpers. The FP parts
 * (number formatting and StockWidget_MainPage_init) are in ui_stock_page_fp.c. */
#include <stdint.h>
#include <stddef.h>

#include "ui_stock_page_private.h"

/* Event pushed to stock_ext_fifo while the expanded page is busy. */
#define STOCK_EXT_EVENT_REFRESH 0x47u

/* Page dots: 4x4 squares stacked 12 px apart, centred in the 254 px frame. */
#define DOT_SIZE 4
#define DOT_GAP 8
#define DOT_AREA_H 254
#define DOT_AREA_Y 17
#define DOT_X (536 + 20 + 3) /* 559 */
#define DOT_INACTIVE_OPA 150u

static const char stock_module_tag[] = "dashboard.stock"; /* ROM 0x789e80 */
static const char stock_source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\screens\\ui_stock_page.c"; /* ROM 0x6f0e98 */

static const char fn_reflash[] = "Stock_Page_Reflash"; /* ROM 0x784aa4 */
static const char reflash_count[] = "Refreshing UI with %d stocks"; /* ROM 0x767d30 */
static const char reflash_count_short[] = "[dashboard.stock]Refreshing UI with %d stocks"; /* ROM 0x73b084 */
static const char reflash_uninit[] = "widget_stock_init_flag == 0, return"; /* ROM 0x75cd74 */
static const char reflash_uninit_short[] = "[dashboard.stock]widget_stock_init_flag == 0, return"; /* ROM 0x725db8 */
static const char reflash_null[] = " data is NULL"; /* ROM 0x789e90 */
static const char reflash_null_short[] = "[dashboard.stock] data is NULL"; /* ROM 0x767d50 */
static const char reflash_bad_index[] = "Invalid stock_tilelist_index: %d"; /* ROM 0x75cd98 */
static const char reflash_bad_index_short[] = "[dashboard.stock]Invalid stock_tilelist_index: %d"; /* ROM 0x7306e4 */
static const char reflash_ext[] = " Updating expanded page UI"; /* ROM 0x7743bc */
static const char reflash_ext_short[] = "[dashboard.stock] Updating expanded page UI"; /* ROM 0x7466f0 */
static const char reflash_ext_done[] = "Expanded page UI update completed"; /* ROM 0x75cdbc */
static const char reflash_ext_done_short[] = "[dashboard.stock]Expanded page UI update completed"; /* ROM 0x730718 */
static const char reflash_fifo[] = "stock_ext_fifo is not empty, push event to fifo,code = %d"; /* ROM 0x71b088 */
static const char reflash_fifo_short[] =
    "[dashboard.stock]stock_ext_fifo is not empty, push event to fifo,code = %d"; /* ROM 0x6f7830 */
static const char reflash_done[] = "stock Refresh completed successfully"; /* ROM 0x750edc */
static const char reflash_done_short[] = "[dashboard.stock]stock Refresh completed successfully"; /* ROM 0x725df0 */

static const char fn_calculate[] = "calculate_stocks_in_container"; /* ROM 0x767db0 */
static const char calc_msg[] = "Container %d has %d stocks (total: %d, start: %d)"; /* ROM 0x73074c */
static const char calc_msg_short[] =
    "[dashboard.stock]Container %d has %d stocks (total: %d, start: %d)"; /* ROM 0x708350 */

static const char fn_separator[] = "update_separator_lines_visibility"; /* ROM 0x75cde0 */
static const char sep_null[] = "container is NULL"; /* ROM 0x784ab8 */
static const char sep_null_short[] = "[dashboard.stock]container is NULL"; /* ROM 0x75ce04 */

static const char fn_create_dots[] = "stock_create_page_dots"; /* ROM 0x77d5c4 */
static const char dots_parent_null[] = "parent is NULL"; /* ROM 0x789ea0 */
static const char dots_parent_null_short[] = "[dashboard.stock]parent is NULL"; /* ROM 0x767dd0 */
static const char dots_total[] = "total_stocks = %d"; /* ROM 0x784acc */
static const char dots_total_short[] = "[dashboard.stock]total_stocks = %d"; /* ROM 0x75ce28 */
static const char dots_layout[] =
    "Dots positioning: total_pages=%d, total_height=%d, start_y=%d, dot_x=%d"; /* ROM 0x6ff2cc */
static const char dots_layout_short[] =
    "[dashboard.stock]Dots positioning: total_pages=%d, total_height=%d, start_y=%d, dot_x=%d"; /* ROM 0x6e1fb0 */

static const char fn_update_dots[] = "stock_update_page_dots"; /* ROM 0x77d5dc */
static const char dots_none[] = "No page dots to update"; /* ROM 0x77d5f4 */
static const char dots_none_short[] = "[dashboard.stock]No page dots to update"; /* ROM 0x750f2c */

static const char fn_cleanup[] = "stock_ext_page_cleanup"; /* ROM 0x77d60c */
static const char cleanup_begin[] = "cleanup expanded page all flags and status"; /* ROM 0x746748 */
static const char cleanup_begin_short[] =
    "[dashboard.stock]cleanup expanded page all flags and status"; /* ROM 0x71b0c4 */
static const char cleanup_fifo[] = "Destroyed stock_ext_fifo"; /* ROM 0x774410 */
static const char cleanup_fifo_short[] = "[dashboard.stock]Destroyed stock_ext_fifo"; /* ROM 0x746774 */
static const char cleanup_done[] = "Page cleanup completed successfully"; /* ROM 0x75ce4c */
static const char cleanup_done_short[] = "[dashboard.stock]Page cleanup completed successfully"; /* ROM 0x725e60 */

static const char fn_switch[] = "stock_switch_to_expanded_container"; /* ROM 0x75ce70 */
static const char switch_begin[] = "Switching container frame pointer to expanded view"; /* ROM 0x730780 */
static const char switch_begin_short[] =
    "[dashboard.stock]Switching container frame pointer to expanded view"; /* ROM 0x708394 */
static const char switch_frame[] = "Cleared non-expanded container frame pointer"; /* ROM 0x73b174 */
static const char switch_frame_short[] =
    "[dashboard.stock]Cleared non-expanded container frame pointer"; /* ROM 0x7117a4 */
static const char switch_no_data[] = "Cleared non-expanded no data display pointers"; /* ROM 0x73b1a4 */
static const char switch_no_data_short[] =
    "[dashboard.stock]Cleared non-expanded no data display pointers"; /* ROM 0x7117e4 */
static const char switch_ext_null[] = "Expanded container frame pointer is NULL"; /* ROM 0x7467a0 */
static const char switch_ext_null_short[] =
    "[dashboard.stock]Expanded container frame pointer is NULL"; /* ROM 0x71b100 */
static const char switch_ext_ok[] = "Expanded container frame pointer is valid"; /* ROM 0x7467cc */
static const char switch_ext_ok_short[] =
    "[dashboard.stock]Expanded container frame pointer is valid"; /* ROM 0x71b13c */
static const char switch_dots[] = "Page dots count: %d"; /* ROM 0x784ae0 */
static const char switch_dots_short[] = "[dashboard.stock]Page dots count: %d"; /* ROM 0x750f54 */

int32_t stock_get_container_index_4ebf20(void)
{
    return g2_stock_container_index_20074e38;
}

/* Rebuild the stock tile and, when the expanded page is open, either rebuild
 * it too or queue a refresh event while it is busy. */
int32_t Stock_Page_Reflash_4ebf5c(const void *data)
{
    STOCK_LOG(4u, 0x10400000u, 0x4f9u, fn_reflash, reflash_count, g2_stock_page_data_201308dc.stock_num);
    if (g2_stock_widget_init_flag_20074e2c == 0u) {
        STOCK_LOG(2u, 0x08000000u, 0x4fcu, fn_reflash, reflash_uninit);
        return 0;
    }
    if (data == NULL) {
        STOCK_LOG(1u, 0x04000000u, 0x501u, fn_reflash, reflash_null);
        return -1;
    }
    if (g2_stock_tilelist_index_20004328 >= STOCK_TILE_COUNT) {
        STOCK_LOG(1u, 0x04400000u, 0x506u, fn_reflash, reflash_bad_index, g2_stock_tilelist_index_20004328);
        return -1;
    }

    if (g2_dashboard_tiles[g2_stock_tilelist_index_20004328].frame != NULL)
        audio_uart_page_44d878(g2_dashboard_tiles[g2_stock_tilelist_index_20004328].frame);
    (void)StockWidget_MainPage_init_4ec2dc(g2_stock_tilelist_index_20004328);

    if (g2_stock_ext_active_20074e30 == 1u && g2_stock_ext_fifo_20074e34 != NULL &&
        g2_dashboard_focus_frame != NULL) {
        STOCK_LOG(4u, 0x10000000u, 0x514u, fn_reflash, reflash_ext);
        if (g2_stock_ext_page_20132e48.ext_busy == 0u) {
            audio_uart_page_44d878(g2_dashboard_focus_frame);
            stock_ext_WidgetPage_Create_4eb7b8(g2_dashboard_focus_frame);
            STOCK_LOG(4u, 0x10000000u, 0x51au, fn_reflash, reflash_ext_done);
        } else {
            uint8_t event[5];
            event[0] = STOCK_EXT_EVENT_REFRESH;
            event[1] = 0u;
            event[2] = 0u;
            event[3] = 0u;
            event[4] = 0u;
            (void)ui_common_api_fn_00509ca2(g2_stock_ext_fifo_20074e34, event, sizeof event);
            STOCK_LOG(4u, 0x10400000u, 0x525u, fn_reflash, reflash_fifo, event[0]);
        }
    }
    STOCK_LOG(4u, 0x10000000u, 0x529u, fn_reflash, reflash_done);
    return 0;
}

int32_t calculate_stocks_in_container_4ecfc8(int32_t container_index)
{
    const int32_t total = (int32_t)stock_page_get_count_4e9fd6();
    const int32_t start = container_index * STOCKS_PER_CONTAINER;
    int32_t count = 0;

    for (int32_t i = start; i < start + STOCKS_PER_CONTAINER && i < total; i++)
        count++;
    STOCK_LOG(4u, 0x11000000u, 0x6fcu, fn_calculate, calc_msg, container_index, count, total, start);
    return count;
}

/* Line 1 separates stocks 1/2 and line 2 stocks 2/3 of the container. */
void update_separator_lines_visibility_4ed058(g2_stock_ext_page_t *container, int32_t container_index)
{
    if (container == NULL) {
        STOCK_LOG(1u, 0x04000000u, 0x708u, fn_separator, sep_null);
        return;
    }

    const int32_t count = calculate_stocks_in_container_4ecfc8(container_index);
    if (container->separator_line1 != NULL) {
        if (count >= 2)
            audio_lv_object_clear_flag_43dfa4(container->separator_line1, LV_OBJ_FLAG_HIDDEN);
        else
            audio_lv_object_flag_43ded4(container->separator_line1, LV_OBJ_FLAG_HIDDEN);
    }
    if (container->separator_line2 != NULL) {
        if (count >= 3)
            audio_lv_object_clear_flag_43dfa4(container->separator_line2, LV_OBJ_FLAG_HIDDEN);
        else
            audio_lv_object_flag_43ded4(container->separator_line2, LV_OBJ_FLAG_HIDDEN);
    }
}

uint8_t stock_page_dots_visible_4ed0ec(void)
{
    return g2_stock_page_dots_visible_20075042;
}

static void style_dot(void *dot, int32_t index)
{
    if (index == stock_get_container_index_4ebf20()) {
        audio_uart_page_44127e(dot, audio_lv_color_44104c(STOCK_WHITE), 0u);
        audio_uart_page_44129e(dot, LV_OPA_COVER, 0u);
    } else {
        audio_uart_page_44127e(dot, audio_lv_color_44104c(STOCK_GREY), 0u);
        audio_uart_page_44129e(dot, DOT_INACTIVE_OPA, 0u);
    }
}

/* One dot per three stocks, at most three dots, only when there is more than
 * one page. */
void stock_create_page_dots_4ed12c(void *parent)
{
    if (parent == NULL) {
        STOCK_LOG(1u, 0x04000000u, 0x72cu, fn_create_dots, dots_parent_null);
        return;
    }

    const uint16_t total_stocks = stock_page_get_count_4e9fd6();
    STOCK_LOG(3u, 0x0c400000u, 0x732u, fn_create_dots, dots_total, total_stocks);

    uint16_t total_pages = (uint16_t)(((int32_t)total_stocks + 2) / 3);
    if (total_pages < 2u) {
        g2_stock_page_dots_count_20074e5c = 0;
        g2_stock_page_dots_visible_20075042 = 0u;
        return;
    }
    g2_stock_page_dots_visible_20075042 = 1u;
    if (total_pages > STOCK_PAGE_DOTS_MAX)
        total_pages = STOCK_PAGE_DOTS_MAX;
    g2_stock_page_dots_count_20074e5c = total_pages;

    const int32_t total_height = (int32_t)total_pages * DOT_SIZE + ((int32_t)total_pages - 1) * DOT_GAP;
    const int32_t start_y = (DOT_AREA_H - total_height) / 2 + DOT_AREA_Y;
    const int32_t dot_x = DOT_X;
    STOCK_LOG(4u, 0x11000000u, 0x759u, fn_create_dots, dots_layout, total_pages, total_height, start_y, dot_x);

    for (int32_t i = 0; i < (int32_t)total_pages; i++) {
        void **const dots = g2_stock_page_dots_200740e0;
        dots[i] = audio_uart_page_43de82(parent);
        audio_lv_object_size_call_43f4c0(dots[i], DOT_SIZE, DOT_SIZE);
        audio_lv_object_position_43f09a(dots[i], dot_x, start_y + i * (DOT_GAP + DOT_SIZE));
        audio_uart_page_44131c(dots[i], 0, 0u);
        audio_uart_page_44146a(dots[i], 0, 0u);
        audio_uart_page_44130c(dots[i], 0u, 0u);
        style_dot(dots[i], i);
        audio_lv_object_clear_flag_43dfa4(dots[i], LV_OBJ_FLAG_CLICKABLE);
    }
}

void stock_update_page_dots_4ed37c(void)
{
    if (g2_stock_page_dots_count_20074e5c == 0) {
        g2_stock_page_dots_visible_20075042 = 0u;
        STOCK_LOG(4u, 0x10000000u, 0x780u, fn_update_dots, dots_none);
        return;
    }
    g2_stock_page_dots_visible_20075042 = 1u;
    for (int32_t i = 0; i < g2_stock_page_dots_count_20074e5c; i++) {
        void **const dots = g2_stock_page_dots_200740e0;
        if (dots[i] != NULL)
            style_dot(dots[i], i);
    }
}

void stock_ext_page_cleanup_4ed440(void)
{
    STOCK_LOG(4u, 0x10000000u, 0x79eu, fn_cleanup, cleanup_begin);
    g2_stock_ext_page_20132e48.ext_busy = 0u;
    g2_stock_ext_active_20074e30 = 0u;
    if (g2_stock_ext_fifo_20074e34 != NULL) {
        ui_common_api_fn_00509c96(g2_stock_ext_fifo_20074e34);
        g2_stock_ext_fifo_20074e34 = NULL;
        STOCK_LOG(4u, 0x10000000u, 0x7a7u, fn_cleanup, cleanup_fifo);
    }
    for (int32_t i = 0; i < (int32_t)STOCK_PAGE_DOTS_MAX; i++)
        g2_stock_page_dots_200740e0[i] = NULL;
    g2_stock_page_dots_count_20074e5c = 0;
    STOCK_LOG(4u, 0x10000000u, 0x7b0u, fn_cleanup, cleanup_done);
}

/* Drops the non-expanded widgets' pointers (the objects themselves are
 * deleted with the tile) and reports the expanded frame state. */
void stock_switch_to_expanded_container_4ed52e(void)
{
    STOCK_LOG(4u, 0x10000000u, 0x7b8u, fn_switch, switch_begin);
    if (g2_stock_container_frame_20074e3c != NULL) {
        g2_stock_container_frame_20074e3c = NULL;
        STOCK_LOG(4u, 0x10000000u, 0x7bdu, fn_switch, switch_frame);
    }
    g2_stock_no_data_icon_20074e44 = NULL;
    g2_stock_no_data_label1_20074e48 = NULL;
    g2_stock_no_data_label2_20074e4c = NULL;
    STOCK_LOG(4u, 0x10000000u, 0x7c4u, fn_switch, switch_no_data);
    if (g2_stock_ext_container_frame_20074e40 == NULL)
        STOCK_LOG(2u, 0x08000000u, 0x7c8u, fn_switch, switch_ext_null);
    else
        STOCK_LOG(4u, 0x10000000u, 0x7cau, fn_switch, switch_ext_ok);
    STOCK_LOG(4u, 0x10400000u, 0x7ceu, fn_switch, switch_dots, g2_stock_page_dots_count_20074e5c);
}

void stock_page_reset_state_4ed6c4(void)
{
    g2_stock_ext_active_20074e30 = 0u;
    g2_stock_ext_page_20132e48.ext_busy = 0u;
    g2_stock_page_dots_count_20074e5c = 0;
    g2_stock_widget_init_flag_20074e2c = 0u;
}
