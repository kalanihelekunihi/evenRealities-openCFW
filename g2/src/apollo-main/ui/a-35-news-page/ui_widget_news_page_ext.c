/* Dashboard news widget, expanded ("ext") list page and state resets, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\screens\ui_widget_news_page.c.
 * Native 0x4f4670..0x4f4eb9 (News_Widget_ext_init), 0x4f4ed8..0x4f4f3b and
 * 0x4f4f3c..0x4f4f5b; literal pool 0x4f4f5c..0x4f504f (0x4f4ebc..0x4f4ed7 belongs
 * to NewsInputEventHandler 0x4f4030). The other functions of this TU are in
 * ui/a-33-widget-news-page.
 *
 * The ext page is a 576x288 black mask layer on the expanded-page parent with a
 * vertical scroll container (pad left 8, right 14, bottom 288, radius 6, white
 * 1 px scrollbar at opa 127). When all five news records are valid, one item per
 * record is stacked 10 px apart, followed by the "scroll to refresh" end item;
 * otherwise a centred icon + two-line "no news" placeholder is shown. */
#include <stdint.h>
#include <stddef.h>

#define NEWS_RECORDS 5
#define NEWS_ITEM_GAP 10
#define NEWS_SCROLL_PAD_LEFT 8
#define NEWS_SCROLL_PAD_RIGHT 14
#define NEWS_SCROLL_RADIUS 6
#define NEWS_EMPTY_ICON_SIZE 24

#define SCREEN_W 0x240
#define SCREEN_H 0x120
#define LV_SIZE_CONTENT 0x3fffffff
#define LV_PART_SCROLLBAR 0x10000u
#define LV_OBJ_FLAG_SCROLLABLE 0x10u
#define LV_OBJ_FLAG_ADV_HITTEST 0x10000u
#define LV_DIR_VER 0x0cu
#define LV_SCROLLBAR_MODE_AUTO 3u
#define LV_ALIGN_CENTER 9u
#define LV_FLEX_FLOW_ROW 0u
#define LV_FLEX_FLOW_COLUMN 1u
#define LV_FLEX_ALIGN_CENTER 2u
#define LV_TEXT_ALIGN_CENTER 2u
#define COLOR_BLACK 0x000000u
#define COLOR_WHITE 0xffffffu
#define WAIT_FOREVER 0xffffffffu

typedef struct {
    uint8_t valid;          /* +0x0000 1 = record present */
    char title[0x80];       /* +0x0001 */
    char content[0x1c0f];   /* +0x0081 */
    uint64_t timestamp_ms;  /* +0x1c90 */
} g2_news_record_t;
_Static_assert(sizeof(g2_news_record_t) == 0x1c98u, "news record");

extern uint8_t g2_dashboard_news_cache_20132f74[0x8ef8];  /* RAM 0x20132f74, 5 records */
extern uint8_t g2_news_staging_203024a4[0x8f48];          /* RAM 0x203024a4 */
extern void *g2_dashboard_mutex_200743a8;                 /* RAM 0x200743a8 osMutexId */
extern uint32_t audio_uart_ring_primary_head_cell;        /* RAM 0x200746dc: active lv_font_t * */
extern int32_t g2_news_widget_init_flag_20074e60;         /* RAM 0x20074e60 */
extern int32_t g2_news_tile_index_2000432c;               /* RAM 0x2000432c (initialised data) */
extern int32_t g2_news_widget_state_20074e64;             /* RAM 0x20074e64 1 = ext page built */
extern int32_t g2_news_expanded_20074e68;                 /* RAM 0x20074e68 */
extern void *g2_news_ext_fifo_20074e6c;                   /* RAM 0x20074e6c */
extern void *g2_news_list_page_20074e70;                  /* RAM 0x20074e70 mask layer */
extern void *g2_news_scroll_container_20074e74;           /* RAM 0x20074e74 */
extern int32_t g2_news_selected_index_20074e78;           /* RAM 0x20074e78 */
extern int32_t g2_news_item_count_20074e7c;               /* RAM 0x20074e7c */
extern void *g2_news_end_item_20074e80;                   /* RAM 0x20074e80 */
extern int32_t g2_news_anim_running_20074e88;             /* RAM 0x20074e88 */
extern int32_t g2_news_update_animating_20074e8c;                    /* RAM 0x20074e8c */
extern int32_t g2_news_update_timeout_20074e90;                    /* RAM 0x20074e90 */
extern int32_t g2_news_expanding_20074e94;                /* RAM 0x20074e94 */
extern int32_t g2_news_status_shown_20074e98;                    /* RAM 0x20074e98 */
extern int32_t g2_news_status_resume_20074e9c;                    /* RAM 0x20074e9c */
extern void *g2_news_expand_container_20074ea0;           /* RAM 0x20074ea0 */
extern uint32_t g2_news_detail_20074ea4;                  /* RAM 0x20074ea4 */
extern uint32_t g2_news_detail_20074ea8;                  /* RAM 0x20074ea8 */
extern uint32_t g2_news_detail_20074eac;                  /* RAM 0x20074eac */
extern uint32_t g2_news_detail_20074eb0;                  /* RAM 0x20074eb0 */
extern uint32_t g2_news_detail_20074eb4;                  /* RAM 0x20074eb4 */
extern uint32_t g2_news_detail_20074eb8;                  /* RAM 0x20074eb8 */
extern uint32_t g2_news_detail_20074ebc;                  /* RAM 0x20074ebc */
extern uint32_t g2_news_detail_20074ec0;                  /* RAM 0x20074ec0 */
extern int32_t g2_news_detail_scrolling_20074ec4;                    /* RAM 0x20074ec4 */
extern void *g2_news_items_20073d9c[NEWS_RECORDS];        /* RAM 0x20073d9c list item objects */

extern const uint8_t news_icon_76e7c0[];                  /* ROM 0x76e7c0 lv_image_dsc_t 24x24 */

extern int32_t osMutexAcquire(void *mutex, uint32_t timeout);   /* 0x4497b6 */
extern int32_t osMutexRelease(void *mutex);                     /* 0x44981c */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* memset 0x43c0e4 */
extern void *ui_common_api_fn_00509c1c(void);                   /* fifo create */
extern void ui_common_api_fn_00509c96(void *fifo);              /* fifo destroy */
extern void *audio_uart_page_43de82(void *parent);              /* lv_obj_create */
extern void audio_uart_page_43ded4(void *obj, uint32_t flag);   /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flag);   /* lv_obj_remove_flag */
extern void audio_uart_page_43f09a(void *obj, int32_t x, int32_t y); /* lv_obj_set_pos */
extern void audio_uart_page_43f4c0(void *obj, int32_t w, int32_t h); /* lv_obj_set_size */
extern void audio_uart_page_43f506(void *obj, int32_t w);       /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *obj, int32_t h);       /* lv_obj_set_height */
extern void audio_uart_page_43f66c(void *obj);                  /* lv_obj_update_layout */
extern void lv_obj_align_43f6b8(void *obj, uint32_t align, int32_t x, int32_t y);
extern int32_t audio_uart_lv_obj_y_43fce0(void *obj);           /* lv_obj_get_y */
extern int32_t audio_uart_lv_obj_height_43fdda(void *obj);      /* lv_obj_get_height */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);           /* lv_color_hex */
extern void audio_uart_page_441164(void *obj, int32_t v, uint32_t sel);  /* style width */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel);  /* style pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel);  /* style pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel);  /* style pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel);  /* style pad_right */
extern void audio_uart_page_441246(void *obj, int32_t v, uint32_t sel);  /* style pad_row */
extern void audio_uart_page_441254(void *obj, int32_t v, uint32_t sel);  /* style pad_column */
extern void audio_uart_page_44127e(void *obj, uint32_t c, uint32_t sel); /* style bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t v, uint32_t sel); /* style bg_opa */
extern void audio_uart_page_4412ec(void *obj, uint32_t c, uint32_t sel); /* style border_color */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t sel);  /* style border_width */
extern void audio_uart_page_44140e(void *obj, uint32_t c, uint32_t sel); /* style text_color */
extern void audio_uart_page_44143e(void *obj, uint32_t font, uint32_t sel); /* style text_font */
extern void audio_uart_page_44145a(void *obj, uint32_t v, uint32_t sel); /* style text_align */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);  /* style radius */
extern void audio_uart_page_44e368(void *obj, uint32_t mode);   /* lv_obj_set_scrollbar_mode */
extern void audio_uart_page_44e3ca(void *obj, uint32_t dir);    /* lv_obj_set_scroll_dir */
extern void audio_uart_lv_scroll_to_y_44ea04(void *obj, int32_t y, uint32_t anim); /* lv_obj_scroll_to_y */
extern uint32_t audio_uart_page_460084(const char *key);        /* i18n index of key */
extern const char *audio_uart_page_45fffe(const char *key, uint32_t index); /* localized text */
extern void audio_uart_page_48ba78(void *obj, uint32_t flow);   /* lv_obj_set_flex_flow */
extern void audio_uart_page_48ba92(void *obj, uint32_t main, uint32_t cross, uint32_t track); /* lv_obj_set_flex_align */
extern void *audio_uart_page_498668(void *parent);              /* lv_image_create */
extern void audio_uart_page_498680(void *img, const void *src); /* lv_image_set_src */
extern void *audio_uart_page_499416(void *parent);              /* lv_label_create */
extern void audio_uart_page_49942e(void *label, const char *text); /* lv_label_set_text */
extern void notifyAppNewsStatus_4fe1b4(uint32_t status, uint32_t arg); /* dashboard_data_process.c notifyAppNewsStatus */
extern uint32_t audio_log_flags(void);                          /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...);              /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* Same TU (ui/a-33-widget-news-page). */
extern void lv_obj_set_style_pad_all_4effa8(void *obj, int32_t value, uint32_t selector);
extern int32_t news_valid_count_4effda(void);
extern void *widget_news_create_item_4f0998(void *parent, const g2_news_record_t *news, int32_t y);
extern void *widget_news_create_refresh_item_4f0cc0(void *parent, int32_t y);
extern void widget_news_show_item_border_4f0e18(int32_t index);

int32_t News_Widget_ext_init_4f4670(void *parent);
void news_widget_deinit_4f4ed8(void);
void news_page_reset_4f4f3c(void);

static const char module_tag[] = "dashborad.news.widget"; /* ROM 0x77d624 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\screens\\ui_widget_news_page.c"; /* ROM 0x6eae4c */
static const char fn_ext_init[] = "News_Widget_ext_init"; /* ROM 0x77d6cc */
static const char parent_null[] = "parent_obj is NULL"; /* ROM 0x784b1c */
static const char parent_null_short[] = "[dashborad.news.widget]parent_obj is NULL"; /* ROM 0x746a34 */
static const char fifo_failed[] = "widget_news_ext_init: Failed to create event FIFO"; /* ROM 0x730b28 */
static const char fifo_failed_short[] =
    "[dashborad.news.widget]widget_news_ext_init: Failed to create event FIFO"; /* ROM 0x6f7c0c */
static const char fifo_created[] = "widget_news_ext_init: Event FIFO created successfully"; /* ROM 0x726058 */
static const char fifo_created_short[] =
    "[dashborad.news.widget]widget_news_ext_init: Event FIFO created successfully"; /* ROM 0x6f1118 */
static const char mask_failed[] = "Failed to create mask layer"; /* ROM 0x7745b4 */
static const char mask_failed_short[] = "[dashborad.news.widget]Failed to create mask layer"; /* ROM 0x730b5c */
static const char scroll_failed[] = "Failed to create scroll container"; /* ROM 0x75d0b0 */
static const char scroll_failed_short[] = "[dashborad.news.widget]Failed to create scroll container"; /* ROM 0x71b394 */
static const char end_created[] = "End item created at y=%d, height=%d, total_content_height=%d"; /* ROM 0x711ae4 */
static const char end_created_short[] =
    "[dashborad.news.widget]End item created at y=%d, height=%d, total_content_height=%d"; /* ROM 0x6eaef4 */
static const char end_failed[] = "Failed to create end_item"; /* ROM 0x7745d0 */
static const char end_failed_short[] = "[dashborad.news.widget]Failed to create end_item"; /* ROM 0x730b90 */
static const char scrolled_to[] = "Scrolled to remembered index %d, y=%d"; /* ROM 0x7511fc */
static const char scrolled_to_short[] = "[dashborad.news.widget]Scrolled to remembered index %d, y=%d"; /* ROM 0x711b24 */
static const char no_news[] = "No valid news data for extension page"; /* ROM 0x751224 */
static const char no_news_short[] = "[dashborad.news.widget]No valid news data for extension page"; /* ROM 0x711b64 */
static const char empty_mask_failed[] = "Failed to create mask layer for empty state"; /* ROM 0x746a60 */
static const char empty_mask_failed_short[] =
    "[dashborad.news.widget]Failed to create mask layer for empty state"; /* ROM 0x708680 */
static const char id_default_1[] = "ID_DASHBOARD_NEWS_DEFAULT_1"; /* ROM 0x7745ec */
static const char id_default_2[] = "ID_DASHBOARD_NEWS_DEFAULT_2"; /* ROM 0x774608 */
static const char init_done[] = "News extension page initialized successfully, %d items created"; /* ROM 0x711ba4 */
static const char init_done_short[] =
    "[dashborad.news.widget]News extension page initialized successfully, %d items created"; /* ROM 0x6e5be8 */

/* Stock log macro expansion: full record when flag bit 1 is set, compressed
 * record when bit 0 or bit 2 is set. */
#define NEWS_LOG(level, line, cflags, msg, msg_short, ...)                                         \
    do {                                                                                            \
        if ((audio_log_flags() & 2u) != 0u)                                                         \
            audio_log_extended((level), module_tag, source_file, fn_ext_init, (line), (msg),        \
                               ##__VA_ARGS__);                                                      \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                       \
            (void)compress_log_output((cflags), (msg_short), (msg_short), ##__VA_ARGS__);            \
    } while (0)

#define NEWS ((const g2_news_record_t *)(const void *)g2_dashboard_news_cache_20132f74)

static const char *i18n(const char *key)
{
    return audio_uart_page_45fffe(key, audio_uart_page_460084(key));
}

/* Full-screen mask layer shared by the list and the empty state. */
static void style_mask_layer(void *mask, uint32_t bg_opa)
{
    audio_uart_page_43f4c0(mask, SCREEN_W, SCREEN_H);
    audio_uart_page_43f09a(mask, -1, -1);
    audio_uart_page_44127e(mask, audio_uart_page_44104c(COLOR_BLACK), 0u);
    audio_uart_page_44129e(mask, bg_opa, 0u);
    audio_uart_page_44131c(mask, 0, 0u);
    lv_obj_set_style_pad_all_4effa8(mask, 0, 0u);
    audio_uart_page_44146a(mask, 0, 0u);
    audio_uart_page_43dfa4(mask, LV_OBJ_FLAG_SCROLLABLE);
}

/* Transparent, borderless, padding-free flex box sized to its content. */
static void style_flex_box(void *box, uint32_t flow)
{
    audio_uart_page_43f4c0(box, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    audio_uart_page_44129e(box, 0u, 0u);
    audio_uart_page_44131c(box, 0, 0u);
    lv_obj_set_style_pad_all_4effa8(box, 0, 0u);
    audio_uart_page_48ba78(box, flow);
    audio_uart_page_48ba92(box, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
}

int32_t News_Widget_ext_init_4f4670(void *parent)
{
    int32_t valid;
    int32_t content_h = 0;

    if (parent == NULL) {
        NEWS_LOG(1u, 2121u, 0x04000000u, parent_null, parent_null_short);
        return -1;
    }
    if (g2_news_ext_fifo_20074e6c != NULL) {
        ui_common_api_fn_00509c96(g2_news_ext_fifo_20074e6c);
        g2_news_ext_fifo_20074e6c = NULL;
    }
    g2_news_ext_fifo_20074e6c = ui_common_api_fn_00509c1c();
    if (g2_news_ext_fifo_20074e6c == NULL) {
        NEWS_LOG(1u, 2134u, 0x04000000u, fifo_failed, fifo_failed_short);
        return -1;
    }
    NEWS_LOG(4u, 2137u, 0x10000000u, fifo_created, fifo_created_short);

    g2_news_list_page_20074e70 = NULL;
    g2_news_scroll_container_20074e74 = NULL;
    g2_news_selected_index_20074e78 = 0;
    g2_news_item_count_20074e7c = 0;
    g2_news_end_item_20074e80 = NULL;
    g2_news_anim_running_20074e88 = 0;
    g2_news_detail_scrolling_20074ec4 = 0;
    g2_news_update_animating_20074e8c = 0;
    g2_news_expanding_20074e94 = 0;
    g2_news_status_shown_20074e98 = 0;
    g2_news_status_resume_20074e9c = 0;
    g2_news_expanded_20074e68 = 0;
    for (int32_t i = 0; i < NEWS_RECORDS; ++i)
        g2_news_items_20073d9c[i] = NULL;
    g2_news_expand_container_20074ea0 = NULL;
    g2_news_detail_20074ea4 = 0u;
    g2_news_detail_20074ea8 = 0u;
    g2_news_detail_20074eac = 0u;
    g2_news_detail_20074eb0 = 0u;
    g2_news_detail_20074eb4 = 0u;
    g2_news_detail_20074eb8 = 0u;
    g2_news_detail_20074ebc = 0u;
    g2_news_detail_20074ec0 = 0u;

    (void)osMutexAcquire(g2_dashboard_mutex_200743a8, WAIT_FOREVER);
    valid = news_valid_count_4effda();
    (void)osMutexRelease(g2_dashboard_mutex_200743a8);

    if (valid == NEWS_RECORDS) {
        void *mask;
        void *scroll;

        mask = audio_uart_page_43de82(parent);
        g2_news_list_page_20074e70 = mask;
        if (mask == NULL) {
            NEWS_LOG(1u, 2178u, 0x04000000u, mask_failed, mask_failed_short);
            return -1;
        }
        style_mask_layer(mask, 0xffu);

        scroll = audio_uart_page_43de82(mask);
        g2_news_scroll_container_20074e74 = scroll;
        if (scroll == NULL) {
            NEWS_LOG(1u, 2196u, 0x04000000u, scroll_failed, scroll_failed_short);
            return -1;
        }
        audio_uart_page_43f4c0(scroll, SCREEN_W, SCREEN_H);
        audio_uart_page_43f09a(scroll, 0, 0);
        audio_uart_page_44129e(scroll, 0u, 0u);
        audio_uart_page_44131c(scroll, 0, 0u);
        audio_uart_page_4412ec(scroll, audio_uart_page_44104c(COLOR_BLACK), 0u);
        audio_uart_page_44146a(scroll, NEWS_SCROLL_RADIUS, 0u);
        audio_uart_page_44122a(scroll, NEWS_SCROLL_PAD_LEFT, 0u);
        audio_uart_page_441238(scroll, NEWS_SCROLL_PAD_RIGHT, 0u);
        audio_uart_page_44120e(scroll, 0, 0u);
        audio_uart_page_44121c(scroll, SCREEN_H, 0u);
        audio_uart_page_44e3ca(scroll, LV_DIR_VER);
        audio_uart_page_44e368(scroll, LV_SCROLLBAR_MODE_AUTO);
        audio_uart_page_441164(scroll, 1, LV_PART_SCROLLBAR);
        audio_uart_page_44127e(scroll, audio_uart_page_44104c(COLOR_WHITE), LV_PART_SCROLLBAR);
        audio_uart_page_44129e(scroll, 0x7fu, LV_PART_SCROLLBAR);

        (void)osMutexAcquire(g2_dashboard_mutex_200743a8, WAIT_FOREVER);
        /* The stock call also passes the running item count in r3 (unused by 0x4f0998). */
        for (int32_t i = 0; i < valid && g2_news_item_count_20074e7c < NEWS_RECORDS; ++i) {
            void *item;
            if (NEWS[i].valid != 1u)
                continue;
            item = widget_news_create_item_4f0998(g2_news_scroll_container_20074e74, &NEWS[i], content_h);
            if (item == NULL)
                continue;
            g2_news_items_20073d9c[g2_news_item_count_20074e7c] = item;
            audio_uart_page_43f66c(item);
            content_h = audio_uart_lv_obj_height_43fdda(item) + content_h + NEWS_ITEM_GAP;
            ++g2_news_item_count_20074e7c;
        }
        (void)osMutexRelease(g2_dashboard_mutex_200743a8);

        g2_news_end_item_20074e80 =
            widget_news_create_refresh_item_4f0cc0(g2_news_scroll_container_20074e74, content_h);
        if (g2_news_end_item_20074e80 != NULL) {
            int32_t end_h;
            audio_uart_page_43f66c(g2_news_end_item_20074e80);
            end_h = audio_uart_lv_obj_height_43fdda(g2_news_end_item_20074e80);
            content_h = end_h + content_h;
            if ((audio_log_flags() & 2u) != 0u)
                audio_log_extended(3u, module_tag, source_file, fn_ext_init, 2252u, end_created,
                                   audio_uart_lv_obj_y_43fce0(g2_news_end_item_20074e80), end_h,
                                   content_h);
            if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
                (void)compress_log_output(0x0cc00000u, end_created_short, end_created_short,
                                          audio_uart_lv_obj_y_43fce0(g2_news_end_item_20074e80), end_h,
                                          content_h);
        } else {
            NEWS_LOG(1u, 2254u, 0x04000000u, end_failed, end_failed_short);
        }

        /* The remembered index is reset to 0 first, so the restore below never fires. */
        g2_news_selected_index_20074e78 = 0;
        if (g2_news_selected_index_20074e78 >= 1 &&
            g2_news_selected_index_20074e78 < g2_news_item_count_20074e7c &&
            g2_news_items_20073d9c[g2_news_selected_index_20074e78] != NULL) {
            const int32_t y =
                audio_uart_lv_obj_y_43fce0(g2_news_items_20073d9c[g2_news_selected_index_20074e78]);
            audio_uart_lv_scroll_to_y_44ea04(g2_news_scroll_container_20074e74, y, 0u);
            NEWS_LOG(4u, 2264u, 0x10800000u, scrolled_to, scrolled_to_short,
                     g2_news_selected_index_20074e78, y);
        }
        widget_news_show_item_border_4f0e18(g2_news_selected_index_20074e78);
    } else {
        void *mask;
        void *column;
        void *row;
        void *icon;
        void *label;

        NEWS_LOG(4u, 2274u, 0x10000000u, no_news, no_news_short);
        mask = audio_uart_page_43de82(parent);
        g2_news_list_page_20074e70 = mask;
        if (mask == NULL) {
            NEWS_LOG(1u, 2279u, 0x04000000u, empty_mask_failed, empty_mask_failed_short);
            return -1;
        }
        style_mask_layer(mask, 0u);

        column = audio_uart_page_43de82(g2_news_list_page_20074e70);
        style_flex_box(column, LV_FLEX_FLOW_COLUMN);
        audio_uart_page_441246(column, 6, 0u);
        lv_obj_align_43f6b8(column, LV_ALIGN_CENTER, 0, 0);

        row = audio_uart_page_43de82(column);
        style_flex_box(row, LV_FLEX_FLOW_ROW);
        audio_uart_page_441254(row, 8, 0u);

        icon = audio_uart_page_498668(row);
        audio_uart_page_498680(icon, news_icon_76e7c0);
        audio_uart_page_43f506(icon, NEWS_EMPTY_ICON_SIZE);
        audio_uart_page_43f568(icon, NEWS_EMPTY_ICON_SIZE);
        audio_uart_page_43ded4(icon, LV_OBJ_FLAG_ADV_HITTEST);
        audio_uart_page_43dfa4(icon, LV_OBJ_FLAG_SCROLLABLE);

        label = audio_uart_page_499416(row);
        audio_uart_page_49942e(label, i18n(id_default_1));
        audio_uart_page_44140e(label, audio_uart_page_44104c(COLOR_WHITE), 0u);
        audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, 0u);

        label = audio_uart_page_499416(column);
        audio_uart_page_49942e(label, i18n(id_default_2));
        audio_uart_page_44140e(label, audio_uart_page_44104c(COLOR_WHITE), 0u);
        audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, 0u);
        audio_uart_page_44145a(label, LV_TEXT_ALIGN_CENTER, 0u);
    }

    g2_news_widget_state_20074e64 = 1;
    notifyAppNewsStatus_4fe1b4(0u, 0u);
    NEWS_LOG(3u, 2337u, 0x0c400000u, init_done, init_done_short, g2_news_item_count_20074e7c);
    return 0;
}

void news_widget_deinit_4f4ed8(void)
{
    g2_news_tile_index_2000432c = -1;
    g2_news_widget_init_flag_20074e60 = 0;
    g2_news_widget_state_20074e64 = 0;
    g2_news_expanded_20074e68 = 0;
    g2_news_list_page_20074e70 = NULL;
    g2_news_scroll_container_20074e74 = NULL;
    g2_news_selected_index_20074e78 = 0;
    g2_news_item_count_20074e7c = 0;
    g2_news_end_item_20074e80 = NULL;
    g2_news_anim_running_20074e88 = 0;
    g2_news_detail_scrolling_20074ec4 = 0;
    g2_news_update_animating_20074e8c = 0;
    g2_news_update_timeout_20074e90 = 0;
    g2_news_expanding_20074e94 = 0;
    g2_news_status_shown_20074e98 = 0;
    g2_news_status_resume_20074e9c = 0;
}

void news_page_reset_4f4f3c(void)
{
    audio_uart_buffer_zero(g2_dashboard_news_cache_20132f74, sizeof g2_dashboard_news_cache_20132f74, 0u);
    audio_uart_buffer_zero(g2_news_staging_203024a4, sizeof g2_news_staging_203024a4, 0u);
}
