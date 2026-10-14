/* Apollo display-driver timer initializer 0x473ad0..0x473b33. Candidate. */
#include <stdint.h>
struct display_driver_timer_attributes {
    const char *name;
    uint32_t flags;
    void *control_block;
    uint32_t control_block_size;
};
_Static_assert(sizeof(struct display_driver_timer_attributes)==16u,"timer attributes ABI");
extern void * volatile display_driver_timer_handle; /* SRAM 0x200744f0 */
extern void *audio_uart_timer_new(void (*)(void *),uint32_t,void *,const void *); /* 0x4493b0 */
extern void display_driver_timer_callback_473b54(void *);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint32_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void compressed_log_output(uint32_t,const char *,const char *,...);
uint8_t display_driver_timer_control_block[44]; /* initialized as BSS at SRAM 0x200735cc */
static const char timer_name[]="display_device_timer";
static const struct display_driver_timer_attributes timer_attrs={
    timer_name,0u,display_driver_timer_control_block,44u};
static const char module[]="task.displaydrvmgr";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\display_mgr\\displaydrv_manager.c";
static const char function[]="display_device_resource_init";
static const char text[]="display_device_timer_id create failed..\r\n";
static const char compact[]="[task.displaydrvmgr]display_device_timer_id create failed..\r\n";
void display_driver_init_473ad0(void) {
    display_driver_timer_handle=audio_uart_timer_new(display_driver_timer_callback_473b54,
                                                      1u,0,&timer_attrs);
    if(display_driver_timer_handle!=0) return;
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(1u,module,path,function,0x9fu,text);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        compressed_log_output(0x04000000u,compact,compact);
}
