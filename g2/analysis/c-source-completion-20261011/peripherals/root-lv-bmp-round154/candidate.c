#include <stdint.h>
extern const char *audio_uart_lv_fs_extension_4c70e4(const char *);
extern int32_t audio_uart_lv_string_compare_4547be(const char *,const char *);
extern void audio_uart_lv_basic_box_clear_454746(void *,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_fs_file_open_4c6d9a(void *,const char *,uint32_t);
extern uint32_t audio_uart_lv_fs_file_read_4c6f46(void *,void *,uint32_t,uint32_t *);
extern uint32_t audio_uart_lv_fs_file_close_4c6ee0(void *);
extern void *audio_uart_lv_grid_copy_454738(void *,const void *,uint32_t);
extern void *audio_uart_lv_malloc(uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
static const char bmp_open_reason[]="Out of memory";
static const char bmp_open_expression[]="dsc->user_data != NULL";
static const char bmp_open_format[]="Asserted at expression: %s (%s)";
static const char bmp_open_function[]="decoder_open";
static const char bmp_open_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\bmp\\lv_bmp.c";
/* Native4c92a8..4c93a0; unsigned wrapped row-size arithmetic. */
uint32_t audio_uart_lv_bmp_open_4c92a8(void *decoder,void *descriptor) {
    (void)decoder;volatile uint8_t *d=descriptor;
    if(d[16]!=1u)return 0u;
    const char *src=(const char *)(uintptr_t)*(volatile uint32_t *)(d+12u);
    if(audio_uart_lv_string_compare_4547be(audio_uart_lv_fs_extension_4c70e4(src),"bmp")!=0)return 0u;
    uint32_t state[8];uint8_t bytes[54];
    audio_uart_lv_basic_box_clear_454746(state,0u,32u);
    src=(const char *)(uintptr_t)*(volatile uint32_t *)(d+12u);
    if((uint8_t)audio_uart_lv_fs_file_open_4c6d9a(state,src,2u)!=0u)return 0u;
    (void)audio_uart_lv_fs_file_read_4c6f46(state,bytes,54u,0);
    if(bytes[0]!=0x42u||bytes[1]!=0x4du) {
        (void)audio_uart_lv_fs_file_close_4c6ee0(state);return 0u;
    }
    audio_uart_lv_grid_copy_454738(state+3,bytes+10u,4u);
    audio_uart_lv_grid_copy_454738(state+4,bytes+18u,4u);
    audio_uart_lv_grid_copy_454738(state+5,bytes+22u,4u);
    audio_uart_lv_grid_copy_454738(state+6,bytes+28u,2u);
    state[7]=((state[6]*state[4]+31u)>>5)<<2;
    *(volatile uint32_t *)(d+72u)=(uint32_t)(uintptr_t)audio_uart_lv_malloc(32u);
    if(*(volatile uint32_t *)(d+72u)==0u) {
        audio_uart_lvgl_log(3u,bmp_open_path,180u,bmp_open_function,bmp_open_format,bmp_open_expression,bmp_open_reason);
        for(;;)*(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    if(*(volatile uint32_t *)(d+72u)==0u)return 0u;
    audio_uart_lv_grid_copy_454738((void *)(uintptr_t)*(volatile uint32_t *)(d+72u),state,32u);
    return 1u;
}
