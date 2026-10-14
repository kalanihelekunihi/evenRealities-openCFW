/* Apollo buffer_sync_to_fb 0x46c73c..0x46c983. Candidate. */
#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
extern void audio_uart_lv_memzero_48949c(void *,uint32_t);
extern void audio_uart_checksum_copy(void *,const void *,uint32_t);
extern uint32_t audio_uart_ambiq_bind_buffer_4b092a(void *,const void *,uint32_t);
extern void display_driver_gpu_mode_4b0730(uint32_t,uint32_t);
extern void display_driver_gpu_clear_4b1a78(uint32_t);
extern void display_driver_gpu_enable_4b0748(uint32_t,uint32_t);
extern void display_driver_gpu_blit_4b1608(void *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern void display_driver_gpu_position_4b1b48(int32_t,uint32_t);
extern uint32_t audio_uart_ambiq_submit_4b0c8a(uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const uint32_t template_words[7]={0x619u,0u,0u,0u,0u,0u,0u};
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\display_preprocess.c";
static const char function[]="buffer_sync_to_fb";
static const char assertion[]="Asserted at expression: %s";
static const char *const conditions[]={
    "ptr_des != NULL","ptr_src != NULL","des_width > src_width",
    "des_hight > src_hight","offset_x % 2 == 0","src_width % 2 == 0",
    "des_width % 2 == 0","((uint32_t)ptr_des & 0x00000007) == 0",
    "((uint32_t)ptr_src & 0x00000007) == 0"
};
static const char module[]="display";
static const char failed[]="GPU start failed, result = %d\r\n";
static const char compact[]="[display]GPU start failed, result = %d\r\n";
static void frame_assert(uint32_t line,const char *condition) {
    audio_uart_lvgl_log(3u,path,line,function,assertion,condition);
    for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
}
void display_driver_frame_prepare_46c73c(void *dest,void *src,uint32_t src_width,
                                          uint32_t src_height,uint32_t dest_width,
                                          uint32_t dest_height,uint32_t offset_x,
                                          uint32_t offset_y) {
    if(dest==0) frame_assert(0x24u,conditions[0]);
    if(src==0) frame_assert(0x25u,conditions[1]);
    if(dest_width>=src_width) frame_assert(0x26u,conditions[2]);
    if(dest_height>=src_height) frame_assert(0x27u,conditions[3]);
    if((offset_x&1u)!=0u) frame_assert(0x28u,conditions[4]);
    if((dest_width&1u)!=0u) frame_assert(0x29u,conditions[5]);
    if((src_width&1u)!=0u) frame_assert(0x2au,conditions[6]);
    if(((uintptr_t)dest&7u)!=0u) frame_assert(0x2bu,conditions[7]);
    if(((uintptr_t)src&7u)!=0u) frame_assert(0x2cu,conditions[8]);

    uint32_t area[4];
    audio_uart_lv_memzero_48949c(area,16u);
    area[2]=(src_width>>1)-1u;
    area[3]=src_height-1u;
    uint32_t descriptor[7];
    audio_uart_checksum_copy(descriptor,template_words,28u);
    descriptor[1]=(descriptor[1]&0xffff0000u)|((src_width>>1)&0xffffu);
    descriptor[1]=(descriptor[1]&0x0000ffffu)|((src_height&0xffffu)<<16);
    descriptor[2]=(descriptor[2]&0xffff0000u)|((src_width>>1)&0xffffu);
    descriptor[3]=(src_width*src_height)>>1;
    descriptor[4]=(uint32_t)(uintptr_t)dest;
    descriptor[5]=(uint32_t)(uintptr_t)dest;
    uint32_t result=audio_uart_ambiq_bind_buffer_4b092a(descriptor,area,0u);
    if((uint8_t)result!=1u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,0x46u,failed,(uint8_t)result);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04400000u,compact,compact,(uint8_t)result);
        return;
    }
    display_driver_gpu_mode_4b0730(0u,1u);
    display_driver_gpu_clear_4b1a78(0u);
    display_driver_gpu_enable_4b0748(0u,1u);
    display_driver_gpu_blit_4b1608(src,dest_width>>1,dest_height,9u,
                                  dest_width>>1,0u);
    display_driver_gpu_position_4b1b48((int32_t)offset_x/2,offset_y);
    (void)audio_uart_ambiq_submit_4b0c8a(1u);
}
