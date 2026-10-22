/* Main menu page construction and event entry points, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\menu\menu_page.c.
 * Native 0x462ea8..0x46300d, 0x46302c..0x4631a9, 0x463204..0x46327d and 0x46327e..0x463b8d (Menu_ui_event_handler,
 * registry row 12 at ROM 0x6a4570, context RAM 0x20002ca8); literal pools 0x462f20..0x462f34,
 * 0x463010..0x463028, 0x4631ac..0x463200 and 0x463b90..0x463c64.
 *
 * Layout: root (W x 288, black) > list frame (W-16 x 288, 1 px white border, radius 6,
 * 19 px top/bottom padding) > scroll viewport (W-16 x 250, vertical scroll) > content
 * (W-16 x count*50+30) > rows (content-sized x 50, at y = 50*i) holding an icon at
 * (16,12) and a label at (52,10). W = widest label + 96, capped at 272 (211 is bumped to 212). */
#include "menu_page_private.h"

#define UI_EVENT_TYPE_INIT 2u
#define UI_EVENT_TYPE_DATA 3u
#define UI_EVENT_TYPE_KEY 4u
#define UI_EVENT_TYPE_EXIT 5u

#define MENU_KEY_SELECT 0x0au
#define MENU_KEY_DOWN 0x44u
#define MENU_KEY_UP 0x45u
#define MENU_KEY_ABSOLUTE 0x46u
#define MENU_KEY_EXIT 0x48u
#define MENU_INDEX_JUMP_EVENT 0xf0u

#define MENU_PAGE_ID 3u
#define DEVICE_ROLE_MASTER 1u
#define DEVICE_ROLE_SLAVE 2u

#define LV_SIZE_CONTENT 0x3fffffff
#define LV_OBJ_FLAG_SCROLLABLE 0x10u
#define LV_DIR_VER 0x0cu
#define LV_SCROLLBAR_MODE_OFF 0u
#define LV_LABEL_LONG_DOT 1u

extern void *audio_uart_page_43de82(void *parent);                          /* lv_obj_create */
extern void audio_uart_page_43ded4(void *obj, uint32_t flags);              /* add_flag */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flags);              /* remove_flag */
extern void audio_uart_page_43f09a(void *obj, int32_t x, int32_t y);        /* set_pos */
extern void audio_uart_page_43f0e0(void *obj, int32_t x);                   /* set_x */
extern void audio_uart_page_43f142(void *obj, int32_t y);                   /* set_y */
extern void audio_uart_page_43f4c0(void *obj, int32_t w, int32_t h);        /* set_size */
extern void audio_uart_page_43f506(void *obj, int32_t w);                   /* set_width */
extern void audio_uart_page_43f568(void *obj, int32_t h);                   /* set_height */
extern void audio_uart_page_43f66c(void *obj);                              /* update_layout */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                       /* lv_color_hex */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t selector); /* pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t selector); /* pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t selector); /* pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t selector); /* pad_right */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t selector); /* bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t opa, uint32_t selector);   /* bg_opa */
extern void audio_uart_page_4412ec(void *obj, uint32_t color, uint32_t selector); /* border_color */
extern void audio_uart_page_44130c(void *obj, uint32_t opa, uint32_t selector);   /* border_opa */
extern void audio_uart_page_44131c(void *obj, int32_t w, uint32_t selector);      /* border_width */
extern void audio_uart_page_4413ce(void *obj, uint32_t opa, uint32_t selector);   /* image_opa */
extern void audio_uart_page_44140e(void *obj, uint32_t color, uint32_t selector); /* text_color */
extern void audio_uart_page_44143e(void *obj, uint32_t font, uint32_t selector);  /* text_font */
extern void audio_uart_page_44146a(void *obj, int32_t r, uint32_t selector);      /* radius */
extern void style_prop_2d_441478(void *obj, uint32_t value, uint32_t selector);   /* style prop 0x2d */
extern uint32_t audio_uart_page_44e368(void *obj, uint32_t mode);           /* scrollbar_mode */
extern uint32_t audio_uart_page_44e3ca(void *obj, uint32_t dir);            /* scroll_dir */
extern void audio_uart_lv_scroll_to_y_44ea04(void *obj, int32_t y, uint32_t animated);
extern uint32_t audio_uart_lv_style_unlink_450500(void *obj, void *arg);    /* anim/style detach */
extern int32_t locale_language_index_44368e(void);
extern int32_t audio_uart_text_line_width_489934(const char *text, uint32_t length,
                                                 const void *font, int32_t letter_spacing);
extern void *audio_uart_page_498668(void *parent);                          /* lv_image_create */
extern void audio_uart_page_498680(void *obj, const void *src);             /* image_set_src */
extern void *audio_uart_page_499416(void *parent);                          /* lv_label_create */
extern const char *audio_uart_page_49942e(void *obj, const char *text);     /* label_set_text */
extern void *audio_uart_page_layout_499678(void *obj, uint32_t mode);       /* label_set_long_mode */
extern uint32_t display_driver_uled_mode_45a568(void);                      /* device role */
extern void audio_uart_master_display_refresh(uint32_t id, const void *payload, uint16_t length,
                                              uint32_t extra);              /* 0x464bb2 */
extern void audio_system_alert_close_464c36(uint32_t app, uint32_t payload, uint32_t len,
                                            uint32_t context);

static const char menu_module_tag[] = "menu.page"; /* ROM 0x78b5b8 */
static const char menu_source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\menu\\menu_page.c"; /* ROM 0x70ca64 */
static const char reflash_fn[] = "Menu_ReflashEventHandler"; /* ROM 0x76e130 */
static const char ui_fn[] = "Menu_ui_event_handler"; /* ROM 0x779724 */

static const char animating_msg[] = "menu_is_animating ,push event to fifo,code = %d"; /* ROM 0x735714 */
static const char animating_msg_s[] =
    "[menu.page]menu_is_animating ,push event to fifo,code = %d"; /* ROM 0x7164d4 */
static const char unknown_msg[] = "unknown menu event code: %d"; /* ROM 0x76e0dc */
static const char unknown_msg_s[] = "[menu.page]unknown menu event code: %d"; /* ROM 0x74b43c */
static const char jump_msg[] =
    "MENU_INDEX_JUMP_EVENT, jump to the corresponding page, index = %d"; /* ROM 0x703b98 */
static const char jump_msg_s[] =
    "[menu.page]MENU_INDEX_JUMP_EVENT, jump to the corresponding page, index = %d"; /* ROM 0x6ee508 */
static const char init_msg[] = "menu_page UI_EVENT_TYPE_INIT"; /* ROM 0x762450 */
static const char init_msg_s[] = "[menu.page]menu_page UI_EVENT_TYPE_INIT"; /* ROM 0x74b48c */
static const char default_msg[] = "use default menu items"; /* ROM 0x77973c */
static const char default_msg_s[] = "[menu.page]use default menu items"; /* ROM 0x756a98 */
static const char ext_msg[] = "use ext menu items"; /* ROM 0x7812a0 */
static const char ext_msg_s[] = "[menu.page]use ext menu items"; /* ROM 0x762470 */
static const char width_msg[] = "container_width == 211"; /* ROM 0x779754 */
static const char width_msg_s[] = "[menu.page]container_width == 211"; /* ROM 0x756abc */
static const char content_msg[] = "menu_content_container initialized: Y=0, height=%d"; /* ROM 0x72ad50 */
static const char content_msg_s[] =
    "[menu.page]menu_content_container initialized: Y=0, height=%d"; /* ROM 0x70cc24 */
static const char height_msg[] = "Content height set to: %d pixels (items: %d * %d)"; /* ROM 0x72ad84 */
static const char height_msg_s[] =
    "[menu.page]Content height set to: %d pixels (items: %d * %d)"; /* ROM 0x70cc64 */
static const char state_msg[] =
    "Initial state: selected_index=%d (%s), scroll_offset=%d, scroll=%d"; /* ROM 0x703bdc */
static const char state_msg_s[] =
    "[menu.page]Initial state: selected_index=%d (%s), scroll_offset=%d, scroll=%d"; /* ROM 0x6ee558 */
static const char done_msg[] = "Menu initialization complete:"; /* ROM 0x762490 */
static const char done_msg_s[] = "[menu.page]Menu initialization complete:"; /* ROM 0x7401b4 */
static const char container_msg[] = "- Container: 225x260, Content height: %d"; /* ROM 0x7401e0 */
static const char container_msg_s[] = "[menu.page]- Container: 225x260, Content height: %d"; /* ROM 0x72adb8 */
static const char items_msg[] = "- Items: %d, Height: %d each"; /* ROM 0x7624b0 */
static const char items_msg_s[] = "[menu.page]- Items: %d, Height: %d each"; /* ROM 0x74b4b4 */
static const char initial_msg[] = "- Initial: selected=%d, scroll_offset=%d"; /* ROM 0x74020c */
static const char initial_msg_s[] = "[menu.page]- Initial: selected=%d, scroll_offset=%d"; /* ROM 0x72adec */
static const char exit_msg[] = "menu DISPLAY_EXIT"; /* ROM 0x7812b4 */
static const char exit_msg_s[] = "[menu.page]menu DISPLAY_EXIT"; /* ROM 0x7624d0 */
static const char reset_msg[] = "Reset menu_content_container Y to 0"; /* ROM 0x756ae0 */
static const char reset_msg_s[] = "[menu.page]Reset menu_content_container Y to 0"; /* ROM 0x735744 */

static const char *menu_item_text(int32_t i)
{
    if (g2_menu_display_items[i].app_type == 0u)
        return MENU_ITEM_TR(i);
    return g2_menu_display_items[i].text;
}

/* Row icon (child 0): the item image, or a 20x20 grey rounded placeholder. */
void *menu_item_icon_create_462ea8(void *parent, int32_t index)
{
    void *img = audio_uart_page_498668(parent);
    if (g2_menu_display_items[index].icon == NULL) {
        audio_uart_page_43f506(img, 20);
        audio_uart_page_43f568(img, 20);
        audio_uart_page_44127e(img, audio_uart_page_44104c(0x444444u), 0u);
        audio_uart_page_44129e(img, 0xffu, 0u);
        audio_uart_page_44146a(img, 4, 0u);
    } else {
        audio_uart_page_498680(img, g2_menu_display_items[index].icon);
        audio_uart_page_43f0e0(img, 16);
        audio_uart_page_43f142(img, 12);
        audio_uart_page_4413ce(img, 0x20u, 0u);
    }
    return img;
}

/* Turns a navigation key into a 6-byte menu event for page 3 (delivered back through
 * UI_EVENT_TYPE_DATA). Byte 2 carries +1/-1 for down/up. Stock also loads
 * context->+0x10 at 0x462f80 and discards it. */
int32_t menu_key_event_send_462f38(uint32_t key, const void *context)
{
    uint8_t event[6];

    if (g2_menu_anim_in_progress != 0u)
        return 0;
    if (key == MENU_KEY_DOWN) {
        event[0] = 0u;
        event[1] = MENU_KEY_DOWN;
        event[2] = 1u;
        event[3] = 0u;
        event[4] = 0u;
        event[5] = 0u;
        audio_uart_master_display_refresh(MENU_PAGE_ID, event, sizeof event, 0u);
        return (int32_t)key; /* stock returns the callee's undefined r0 */
    }
    if (key == MENU_KEY_UP) {
        (void)*(const volatile uint32_t *)(const void *)((const uint8_t *)context + 0x10u);
        event[0] = 0u;
        event[1] = MENU_KEY_UP;
        event[2] = 0xffu;
        event[3] = 0u;
        event[4] = 0u;
        event[5] = 0u;
        audio_uart_master_display_refresh(MENU_PAGE_ID, event, sizeof event, 0u);
        return (int32_t)key;
    }
    if (key == MENU_KEY_SELECT) {
        event[0] = 0u;
        event[1] = MENU_KEY_SELECT;
        event[2] = 0u;
        event[3] = 0u;
        event[4] = 0u;
        event[5] = 0u;
        audio_uart_master_display_refresh(MENU_PAGE_ID, event, sizeof event, 0u);
        return 1;
    }
    if (key == MENU_KEY_EXIT) {
        event[0] = 0u;
        event[1] = MENU_KEY_EXIT;
        event[2] = 0u;
        event[3] = 0u;
        event[4] = 0u;
        event[5] = 0u;
        audio_uart_master_display_refresh(MENU_PAGE_ID, event, sizeof event, 0u);
        return 1;
    }
    return (int32_t)key;
}

/* Native 0x463204..0x46327d: key callback with no TSV row and no direct reference found
 * (no BL and no 0x463205 literal in the image). Only the master forwards menu keys. */
uint32_t menu_key_handler_463204(uint32_t unused0, uint32_t unused1, uint32_t key,
                                 const void *context)
{
    (void)unused0;
    (void)unused1;
    if (key == MENU_KEY_DOWN || key == MENU_KEY_UP || key == MENU_KEY_SELECT || key == MENU_KEY_EXIT) {
        if (display_driver_uled_mode_45a568() == DEVICE_ROLE_SLAVE)
            return 1u;
        (void)menu_key_event_send_462f38(key, context);
    }
    return 1u;
}

/* Data event: {0, code, arg, ...} key codes, or {1, 0xf0, index} jump requests. While an
 * animation runs the 5 bytes after the type byte are queued in the menu FIFO. */
int32_t menu_reflash_event_handler_46302c(const uint8_t *data, uint32_t len)
{
    if (len == 0u)
        return 0;
    if (data[0] == 0u) {
        const uint8_t code = data[1];
        const uint8_t arg = data[2];
        if (g2_menu_anim_in_progress != 0u) {
            MENU_LOG(3u, reflash_fn, 0x60du, 0xc400000u, animating_msg, animating_msg_s, code);
            (void)menu_event_fifo_push_460242(data + 1, 5u);
            return 0;
        }
        switch (code) {
        case MENU_KEY_SELECT:
            menu_inject_event_461620(2u);
            break;
        case MENU_KEY_DOWN:
            menu_inject_event_461620(1u);
            break;
        case MENU_KEY_UP:
            menu_inject_event_461620(0u);
            break;
        case MENU_KEY_ABSOLUTE:
            menu_inject_event_absolute_462594(arg);
            break;
        case MENU_KEY_EXIT:
            if (display_driver_uled_mode_45a568() == DEVICE_ROLE_MASTER)
                audio_system_alert_close_464c36(MENU_PAGE_ID, 0u, 0u, 0u);
            break;
        default:
            MENU_LOG(2u, reflash_fn, 0x629u, 0x8400000u, unknown_msg, unknown_msg_s, code);
            break;
        }
    } else if (data[0] == 1u) {
        const uint8_t index = data[2];
        if (data[1] == MENU_INDEX_JUMP_EVENT) {
            MENU_LOG(4u, reflash_fn, 0x633u, 0x10400000u, jump_msg, jump_msg_s, index);
            menu_jump_to_item_instant_462a7c(index);
        }
    }
    return 0;
}

static void menu_page_init(void *parent)
{
    MENU_LOG(4u, ui_fn, 0x673u, 0x10000000u, init_msg, init_msg_s);
    menu_page_mutex_init_460178();
    menu_page_mutex_lock_46018e();
    if (g2_menu_use_ext_items == 0) {
        MENU_LOG(3u, ui_fn, 0x677u, 0xc000000u, default_msg, default_msg_s);
        g2_menu_item_count = G2_MENU_DEFAULT_ITEM_COUNT;
        (void)audio_queue_copy_bytes(g2_menu_display_items, g2_menu_builtin_apps,
                                     sizeof g2_menu_builtin_apps);
    } else {
        MENU_LOG(3u, ui_fn, 0x67bu, 0xc000000u, ext_msg, ext_msg_s);
        g2_menu_item_count = g2_menu_ext_item_count;
        (void)audio_queue_copy_bytes(g2_menu_display_items, g2_menu_page_items,
                                     (uint32_t)g2_menu_ext_item_count * sizeof(g2_menu_page_item_t));
    }
    menu_page_mutex_unlock_4601ea();
    (void)locale_language_index_44368e();

    const void *font = (const void *)(uintptr_t)audio_uart_ring_secondary_head_cell;
    int32_t width = 0;
    for (int32_t i = 0; i < g2_menu_item_count; i++) {
        const char *text = menu_item_text(i);
        const int32_t w = audio_uart_text_line_width_489934(text, g2_log_module_length(text), font, 0);
        if (width < w)
            width = w;
    }
    width += 0x60;
    if (width > 0x110)
        width = 0x110;
    if (width == 0xd3) {
        MENU_LOG(3u, ui_fn, 0x6a2u, 0xc000000u, width_msg, width_msg_s);
        width = 0xd4;
    }
    const int32_t label_width = width - 0x60;

    g2_menu_focus_anim_obj = audio_uart_page_43de82(parent);
    audio_uart_page_43f506(g2_menu_focus_anim_obj, width);
    audio_uart_page_43f568(g2_menu_focus_anim_obj, 0x120);
    audio_uart_page_43f0e0(g2_menu_focus_anim_obj, 0);
    audio_uart_page_43f142(g2_menu_focus_anim_obj, 0);
    audio_uart_page_43ded4(g2_menu_focus_anim_obj, 0x50000u);
    audio_uart_page_43dfa4(g2_menu_focus_anim_obj, 0x2004u);
    (void)audio_uart_page_44e368(g2_menu_focus_anim_obj, LV_SCROLLBAR_MODE_OFF);
    audio_uart_page_44127e(g2_menu_focus_anim_obj, audio_uart_page_44104c(0u), 0u);
    audio_uart_page_44129e(g2_menu_focus_anim_obj, 0xffu, 0u);
    audio_uart_page_4412ec(g2_menu_focus_anim_obj, audio_uart_page_44104c(0u), 0u);
    audio_uart_page_44131c(g2_menu_focus_anim_obj, 0, 0u);
    style_pad_all_460128(g2_menu_focus_anim_obj, 0, 0u);

    g2_menu_frame_obj = audio_uart_page_43de82(g2_menu_focus_anim_obj);
    audio_uart_page_43f506(g2_menu_frame_obj, width - 0x10);
    audio_uart_page_43f568(g2_menu_frame_obj, 0x120);
    if (display_driver_uled_mode_45a568() == DEVICE_ROLE_MASTER)
        audio_uart_page_43f0e0(g2_menu_frame_obj, 0);
    else if (display_driver_uled_mode_45a568() == DEVICE_ROLE_SLAVE)
        audio_uart_page_43f0e0(g2_menu_frame_obj, 0x10);
    audio_uart_page_43f142(g2_menu_frame_obj, 0);
    (void)audio_uart_page_44e368(g2_menu_frame_obj, LV_SCROLLBAR_MODE_OFF);
    audio_uart_page_43dfa4(g2_menu_frame_obj, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_44129e(g2_menu_frame_obj, 0u, 0u);
    audio_uart_page_44146a(g2_menu_frame_obj, 6, 0u);
    audio_uart_page_4412ec(g2_menu_frame_obj, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44131c(g2_menu_frame_obj, 1, 0u);
    audio_uart_page_44130c(g2_menu_frame_obj, 0xffu, 0u);
    style_prop_2d_441478(g2_menu_frame_obj, 1u, 0u);
    audio_uart_page_44120e(g2_menu_frame_obj, 0x13, 0u);
    audio_uart_page_44121c(g2_menu_frame_obj, 0x13, 0u);
    audio_uart_page_44122a(g2_menu_frame_obj, 0, 0u);
    audio_uart_page_441238(g2_menu_frame_obj, 0, 0u);

    g2_menu_list_obj = audio_uart_page_43de82(g2_menu_frame_obj);
    audio_uart_page_43f506(g2_menu_list_obj, width - 0x10);
    audio_uart_page_43f568(g2_menu_list_obj, 0xfa);
    audio_uart_page_43f09a(g2_menu_list_obj, 0, 0);
    (void)audio_uart_page_44e3ca(g2_menu_list_obj, LV_DIR_VER);
    (void)audio_uart_page_44e368(g2_menu_list_obj, LV_SCROLLBAR_MODE_OFF);
    audio_uart_page_44129e(g2_menu_list_obj, 0u, 0u);
    audio_uart_page_44131c(g2_menu_list_obj, 0, 0u);
    style_pad_all_460128(g2_menu_list_obj, 0, 0u);
    style_prop_2d_441478(g2_menu_list_obj, 1u, 0u);

    g2_menu_content_container = audio_uart_page_43de82(g2_menu_list_obj);
    const int32_t content_height = g2_menu_item_height * g2_menu_item_count + 0x1e;
    audio_uart_page_43f506(g2_menu_content_container, width - 0x10);
    audio_uart_page_43f568(g2_menu_content_container, content_height);
    audio_uart_page_43f0e0(g2_menu_content_container, 0);
    audio_uart_page_43f142(g2_menu_content_container, 0);
    audio_uart_page_44129e(g2_menu_content_container, 0u, 0u);
    audio_uart_page_44131c(g2_menu_content_container, 0, 0u);
    style_pad_all_460128(g2_menu_content_container, 0, 0u);
    audio_uart_page_43dfa4(g2_menu_content_container, LV_OBJ_FLAG_SCROLLABLE);
    (void)audio_uart_lv_style_unlink_450500(g2_menu_content_container, NULL);
    MENU_LOG(4u, ui_fn, 0x6f0u, 0x10400000u, content_msg, content_msg_s, content_height);
    MENU_LOG(4u, ui_fn, 0x6f3u, 0x10c00000u, height_msg, height_msg_s, content_height,
             g2_menu_item_count, g2_menu_item_height);

    for (int32_t i = 0; i < g2_menu_item_count; i++) {
        g2_menu_item_objs[i] = audio_uart_page_43de82(g2_menu_content_container);
        style_pad_all_460128(g2_menu_item_objs[i], 0, 0u);
        audio_uart_page_43f4c0(g2_menu_item_objs[i], LV_SIZE_CONTENT, g2_menu_item_height);
        audio_uart_page_43f0e0(g2_menu_item_objs[i], 10);
        audio_uart_page_43f142(g2_menu_item_objs[i], g2_menu_item_height * i);
        audio_uart_page_44127e(g2_menu_item_objs[i], audio_uart_page_44104c(0u), 0u);
        audio_uart_page_44129e(g2_menu_item_objs[i], 0u, 0u);
        audio_uart_page_44131c(g2_menu_item_objs[i], 0, 0u);
        audio_uart_page_43dfa4(g2_menu_item_objs[i], LV_OBJ_FLAG_SCROLLABLE);

        void *row = g2_menu_item_objs[i];
        (void)menu_item_icon_create_462ea8(row, i);
        void *label = audio_uart_page_499416(row);
        audio_uart_page_43f506(label, label_width);
        audio_uart_page_43f568(label, *(const int32_t *)(const void *)((const uint8_t *)font + 0xc));
        audio_uart_page_43f0e0(label, 0x34);
        audio_uart_page_43f142(label, 10);
        if (g2_menu_display_items[i].app_type == 0u)
            (void)audio_uart_page_49942e(label, MENU_ITEM_TR(i));
        else
            (void)audio_uart_page_49942e(label, g2_menu_display_items[i].text);
        (void)audio_uart_page_layout_499678(label, LV_LABEL_LONG_DOT);
        audio_uart_page_44143e(label, audio_uart_ring_secondary_head_cell, 0u);
        audio_uart_page_44140e(label, audio_uart_page_44104c(0x444444u), 0u);
    }

    g2_menu_current_index = 0;
    g2_menu_scroll_offset = 0;
    audio_uart_page_43f66c(g2_menu_focus_anim_obj);
    const int32_t target = menu_calculate_scroll_position_for_item_460d6c(g2_menu_current_index);
    MENU_LOG(4u, ui_fn, 0x720u, 0x11000000u, state_msg, state_msg_s, g2_menu_current_index,
             MENU_ITEM_TR(g2_menu_current_index), g2_menu_scroll_offset, target);
    audio_uart_lv_scroll_to_y_44ea04(g2_menu_list_obj, target, 0u);
    menu_update_item_styles_462db6();
    menu_item_styles_hook_462db4();
    MENU_LOG(4u, ui_fn, 0x728u, 0x10000000u, done_msg, done_msg_s);
    MENU_LOG(4u, ui_fn, 0x729u, 0x10400000u, container_msg, container_msg_s, content_height);
    MENU_LOG(4u, ui_fn, 0x72au, 0x10800000u, items_msg, items_msg_s, g2_menu_item_count,
             g2_menu_item_height);
    MENU_LOG(4u, ui_fn, 0x72bu, 0x10800000u, initial_msg, initial_msg_s, g2_menu_current_index,
             g2_menu_scroll_offset);
    *(void **)(void *)(audio_uart_registry_context_20002ca8 + 4u) = g2_menu_focus_anim_obj;
}

static void menu_page_exit(void)
{
    MENU_LOG(4u, ui_fn, 0x734u, 0x10000000u, exit_msg, exit_msg_s);
    g2_menu_anim_in_progress = 0u;
    if (g2_menu_content_container != NULL) {
        (void)audio_uart_lv_style_unlink_450500(g2_menu_content_container, NULL);
        audio_uart_page_43f142(g2_menu_content_container, 0);
        MENU_LOG(4u, ui_fn, 0x73bu, 0x10000000u, reset_msg, reset_msg_s);
    }
    if (g2_menu_list_obj != NULL) {
        (void)audio_uart_lv_style_unlink_450500(g2_menu_list_obj, NULL);
        audio_uart_page_43f142(g2_menu_list_obj, 0);
    }
    menu_event_fifo_reset_460344();
    resume_menu_anim_time_460374();
}

/* Menu_ui_event_handler: registry callback for page 3 (menu). */
uint32_t audio_uart_registry_callback_46327e(uint32_t event, const uint8_t *data, uint32_t len,
                                             void *parent)
{
    if (event == UI_EVENT_TYPE_INIT)
        menu_page_init(parent);
    else if (event == UI_EVENT_TYPE_DATA)
        (void)menu_reflash_event_handler_46302c(data, len);
    else if (event != UI_EVENT_TYPE_KEY && event == UI_EVENT_TYPE_EXIT)
        menu_page_exit();
    return 0u;
}
