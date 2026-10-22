/* Apollo page context attachment 0x44d342..0x44d3b1. The list-allocation
 * fatal logger call is source-owned; logger internals remain a separate gate. */
#include <stdint.h>

extern void audio_uart_page_unlink_44d3b2(void *);
extern void audio_uart_lv_obj_setup_layer_43e1fa(void *);
extern void *audio_uart_font_path_node_append(void *);
extern void *audio_uart_lv_list_first(void *);
extern void audio_uart_page_notify_44d5f8(void *);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t, const char *, ...);

static const char page_source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_group.c";
static const char assertion[] = "Asserted at expression: %s (%s)";

