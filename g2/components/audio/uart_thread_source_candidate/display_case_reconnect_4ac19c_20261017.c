/* Stock Main _BoxDetect_TryReconnectRing, 0x4ac19c. */
#include <stdint.h>

extern volatile uint8_t audio_box_reconnect_pending_20075011;
extern volatile uint8_t audio_box_reconnect_suppressed_20075010;
extern void *audio_box_reconnect_timer; /* stock RAM 0x20074924 */
extern int32_t audio_uart_box_reconnect_attempt_4a316c(uint32_t scene);
extern int32_t audio_timer_start(void *timer, uint32_t delay);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,...);

static const char module[]="box.detect";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\box_detect\\service_box_detect.c";
static const char function_name[]="_BoxDetect_TryReconnectRing";

static void log_scene(uint8_t scene, uint32_t line, const char *message, const char *compact)
{
    if (audio_log_level() & 2u)
        audio_log_extended(3u,module,path,function_name,line,message,scene);
    if ((audio_log_level() & 1u) || (audio_log_level() & 4u))
        (void)compressed_log_output(0x0c400000u,compact,compact,scene);
}

void audio_uart_case_force_out_finish_4ac19c(uint32_t scene_arg)
{
    uint8_t scene=(uint8_t)scene_arg;
    if (audio_box_reconnect_pending_20075011 || audio_box_reconnect_suppressed_20075010)
        return;
    if (audio_uart_box_reconnect_attempt_4a316c(scene)) {
        audio_box_reconnect_pending_20075011=1u;
        if (audio_box_reconnect_timer)
            (void)audio_timer_start(audio_box_reconnect_timer,60000u);
        log_scene(scene,0x11du,"[Box] Scene %d: reconnect queued, 60s timeout started",
                  "[box.detect][Box] Scene %d: reconnect queued, 60s timeout started");
    } else {
        log_scene(scene,0x11fu,"[Box] Scene %d: reconnect rejected",
                  "[box.detect][Box] Scene %d: reconnect rejected");
    }
}
