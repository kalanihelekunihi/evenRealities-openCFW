/* Apollo uLED 4-bit framebuffer row cleaner 0x4ca2ac..0x4ca563. */
#include <stdint.h>
extern void *display_driver_uled_context; /* selected source cell 0x200007b8 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected fill provider */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="driver.uled";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\drv_mspi_uled.c";
static const char function[]="uled_clean_fb_data";
static const char error[]="clean frame buffer parameter error!!!";
static const char compact[]="[driver.uled]clean frame buffer parameter error!!!";

uint32_t display_driver_uled_row_callback_4ca2ac(uint8_t fill,uint32_t start_x,
                                                 int32_t start_y,uint32_t end_x,
                                                 int32_t end_y) {
    if((int32_t)end_x>=640)end_x=639u;
    if(end_y>=480)end_y=479;
    if((int32_t)end_x<(int32_t)start_x||end_y<start_y) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,0x128u,error);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04000000u,compact,compact);
        return UINT32_MAX;
    }
    uint8_t *buffer=(uint8_t *)display_driver_uled_context;
    for(int32_t y=start_y;y<=end_y;++y) {
        uint8_t *row=buffer+(uint32_t)y*320u;
        uint32_t first=start_x>>1;
        uint32_t last=end_x>>1;
        if((start_x&1u)==0u) {
            if((end_x&1u)!=0u) {
                audio_uart_buffer_zero(row+first,last-first+1u,fill);
            } else {
                audio_uart_buffer_zero(row+first,last-first,fill);
                row[last]&=0x0fu;
            }
        } else if((end_x&1u)!=0u) {
            audio_uart_buffer_zero(row+first+1u,last-first,fill);
            row[first]&=0xf0u;
        } else {
            audio_uart_buffer_zero(row+first+1u,last-first-1u,fill);
            row[first]&=0xf0u;
            row[last]&=0x0fu;
        }
    }
    return 0u;
}
