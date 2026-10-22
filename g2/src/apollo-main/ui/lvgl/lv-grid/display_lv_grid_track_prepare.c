/* Native LVGL grid calc_cols 0x48cbf8 and calc_rows 0x48cdec. */
#include <stdint.h>
extern uint32_t audio_uart_lv_grid_col_descriptor_48c97c(void *);
extern uint32_t audio_uart_lv_grid_row_descriptor_48c986(void *);
extern void *audio_uart_lv_obj_parent_44dca2(void *);
extern uint32_t audio_uart_lv_grid_col_48c990(void *);
extern uint32_t audio_uart_lv_grid_row_48c99a(void *);
extern uint32_t audio_uart_lv_grid_col_span_48c9a4(void *);
extern uint32_t audio_uart_lv_grid_row_span_48c9ae(void *);
extern uint32_t audio_uart_lv_grid_descriptor_count_48d4d0(const int32_t *);
extern int32_t audio_uart_lv_grid_weight_round_48ca18(int32_t,int32_t);
extern void *audio_uart_lv_malloc(uint32_t);
extern void audio_uart_lv_free(void *);
extern void *audio_uart_lv_grid_copy_454738(void *,const void *,uint32_t);
extern uint32_t audio_uart_lv_child_count_44ddea(void *);
extern void *audio_uart_lv_child_get_44dce2(void *,int32_t);
extern uint32_t audio_uart_lv_obj_has_flag_any_43e11c(void *,uint32_t);
extern int32_t audio_uart_lv_obj_width_43fd9e(void *);
extern int32_t audio_uart_lv_obj_height_43fdda(void *);
extern int32_t audio_uart_lv_obj_content_width_43fe16(void *);
extern int32_t audio_uart_lv_obj_content_height_43fe70(void *);
extern int32_t audio_uart_lv_basic_horizontal_48c860(void *,uint32_t);
extern int32_t audio_uart_lv_basic_vertical_48c856(void *,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);

static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\layouts\\grid\\lv_grid.c";
static const char col_function[]="calc_cols";
static const char row_function[]="calc_rows";
static const char no_col[]="No col descriptor found even on the parent";
static const char no_row[]="No row descriptor found even on the parent";
enum {GRID_CONTENT=0x1fffff9a,GRID_FR_START=0x1fffff9b,GRID_LAST=0x1fffffff};


