/* EvenHub common list container helpers, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenHub\common_list_container.c (log tag
 * "common_list_container"). Native 0x4dccd8..0x4dcd92: static pad-all helper 0x4dccd8,
 * item y position 0x4dcd0a and get_color_from_index 0x4dcd32; literal pool 0x4dd464..0x4dd47c.
 * The rest of the file (common_list_create 0x4dd510, event handling 0x4de354, ...) is
 * reconstructed separately. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define LIST_ITEM_HEIGHT 40
#define LIST_COLOR_COUNT 16u
#define LIST_COLOR_WHITE 0xffffffu

/* Fields of the 0x580-byte list handle read here (see common_list_create). */
typedef struct {
    uint8_t reserved_00[0x58];
    uint32_t item_count;                 /* +0x58 */
    uint32_t reserved_5c;                /* +0x5c */
    uint32_t reserved_60;                /* +0x60 */
    int32_t visible_height;              /* +0x64 height minus 2 * padding */
    int32_t visible_item_count;          /* +0x68 */
    uint8_t center_items;                /* +0x6c 1 when all items fit (no scrolling) */
    uint8_t border_en;                   /* +0x6d */
} common_list_layout_t;
_Static_assert(offsetof(common_list_layout_t, center_items) == 0x6c, "list handle");

/* 16 gray levels 0x000000..0xffffff (ROM 0x709d24). */
static const uint32_t list_gray_colors[LIST_COLOR_COUNT] = {
    0x000000u, 0x111111u, 0x222222u, 0x333333u, 0x444444u, 0x555555u, 0x666666u, 0x777777u,
    0x888888u, 0x999999u, 0xaaaaaau, 0xbbbbbbu, 0xccccccu, 0xddddddu, 0xeeeeeeu, 0xffffffu,
};

/* LVGL style setters (stock copies). */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel); /* pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel); /* pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel); /* pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel); /* pad_right */

/* Logging. */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char list_tag[] = "common_list_container"; /* ROM 0x775a64 */
static const char list_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenHub\\common_list_container.c"; /* ROM 0x6f1fb8 */
static const char fn_color[] = "get_color_from_index"; /* ROM 0x775a4c */
static const char s_bad_color[] =
    "get_color_from_index: invalid color_index %d, using white"; /* ROM 0x712c58 */
static const char s_bad_color_s[] =
    "[common_list_container]get_color_from_index: invalid color_index %d, using white"; /* ROM 0x6e6868 */

/* lv_obj_set_style_pad_all (file-local copy; same body as 0x4935cc / 0x4dbeac). */
void list_obj_set_style_pad_all_4dccd8(void *obj, int32_t value, uint32_t selector)
{
    audio_uart_page_44122a(obj, value, selector);
    audio_uart_page_441238(obj, value, selector);
    audio_uart_page_44120e(obj, value, selector);
    audio_uart_page_44121c(obj, value, selector);
}

/* Y position of item `index`; when the items fit they are centred in the visible height. */
int32_t list_item_y_position_4dcd0a(const common_list_layout_t *list, int32_t index)
{
    if (list->center_items == 0u)
        return index * LIST_ITEM_HEIGHT;
    return LIST_ITEM_HEIGHT * index +
           (list->visible_height - (int32_t)list->item_count * LIST_ITEM_HEIGHT) / 2;
}

/* Gray-level index (0..15) to 0xRRGGBB; out-of-range indexes give white. */
uint32_t get_color_from_index_4dcd32(uint32_t color_index)
{
    if (color_index < LIST_COLOR_COUNT)
        return list_gray_colors[color_index];
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(2, list_tag, list_file, fn_color, 0x9b, s_bad_color, color_index);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x8400000u, s_bad_color_s, s_bad_color_s, color_index);
    return LIST_COLOR_WHITE;
}
