/* Native BoxDetect_Init 0x4ac02a: two one-shot timer lifecycles. */
#include <stdint.h>
struct timer_attributes {const char *name;uint32_t flags;void *control_block;uint32_t control_block_size;};
extern void *audio_box_detect_timer; /* RAM 0x20074920 */
extern void *audio_box_reconnect_timer; /* RAM 0x20074924 */
extern uint8_t audio_box_detect_timer_control_block[44]; /* RAM 0x2007367c */
extern uint8_t audio_box_reconnect_timer_control_block[44]; /* RAM 0x200736a8 */
extern void audio_box_detect_timer_callback_4ac016(void *);
extern void audio_box_reconnect_timer_callback_4ac020(void *);
extern void *audio_uart_timer_new(void (*)(void *),uint32_t,void *,const void *); /* selected 0x4493b0 */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="box.detect";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\box_detect\\service_box_detect.c";
static const char function[]="BoxDetect_Init";
static const char first_name[]="box_detect_out_timer";
static const char second_name[]="ring_reconnect_timer";
static const struct timer_attributes first_attrs={first_name,0u,audio_box_detect_timer_control_block,44u};
static const struct timer_attributes second_attrs={second_name,0u,audio_box_reconnect_timer_control_block,44u};
static void failure(uint32_t line,const char *plain,const char *short_message) {
    if(audio_log_level()&2u)audio_log_extended(1u,module,path,function,line,plain);
    if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x04000000u,short_message,short_message);
}
void audio_box_detect_init_4ac02a(void) {
    if(audio_box_detect_timer==0) {
        audio_box_detect_timer=audio_uart_timer_new(audio_box_detect_timer_callback_4ac016,
                                                    0u,0,&first_attrs);
        if(audio_box_detect_timer==0)
            failure(0xbbu,"Failed to create box detect timer",
                    "[box.detect]Failed to create box detect timer");
    }
    if(audio_box_reconnect_timer==0) {
        audio_box_reconnect_timer=audio_uart_timer_new(audio_box_reconnect_timer_callback_4ac020,
                                                       0u,0,&second_attrs);
        if(audio_box_reconnect_timer==0)
            failure(0xc5u,"Failed to create ring reconnect timer",
                    "[box.detect]Failed to create ring reconnect timer");
    }
}
