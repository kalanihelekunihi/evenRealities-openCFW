/* Native LV global initializer 0x4734cc. The fixed root and product context
 * cell are authenticated RAM; this source does not invent their startup image. */
#include <stdint.h>
#include <stddef.h>
extern uint8_t audio_uart_display_lv_root[]; /* selected RAM0x2006f548 */
extern void *memset(void *,int,size_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\lv_init.c";
static const char function[]="lv_global_init";
static const char format[]="Asserted at expression: %s (%s)";
static const char expression[]="global != NULL";
static const char message[]="NULL pointer";

void audio_uart_lv_array_init_482b00(uint8_t *array,uint32_t bytes)
{
    *(uint32_t *)(void *)array=(bytes+3u)&~3u;
    *(uint32_t *)(void *)(array+4u)=0u;
    *(uint32_t *)(void *)(array+8u)=0u;
}

void audio_uart_lv_init_global_4734cc(volatile uint8_t *global)
{
    if (global==0) {
        audio_uart_lvgl_log(3u,source,0x7cu,function,format,expression,message);
        for (;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    uint8_t *root=(uint8_t *)(void *)global;
    (void)memset(root,0,0x1ecu);
    audio_uart_lv_array_init_482b00(root+4u,796u);
    audio_uart_lv_array_init_482b00(root+68u,220u);
    *(uint32_t *)(void *)(root+100u)=0xa1b2c3d4u;
    root[36u]=1u;
    *(uint32_t *)(void *)(root+88u)=3u;
    *(uint32_t *)(void *)(root+44u)=137u;
    *(uint32_t *)(void *)(root+112u)=66u;
    /* Native 0x4888f6 writes the fixed global root, irrespective of argument. */
    *(uint32_t *)(void *)(audio_uart_display_lv_root+0x68u)=0x1234abcdu;
}
