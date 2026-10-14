/* Apollo Main native 0x473952 and 0x4739fc, displaydrv_manager callbacks.
 * Exploratory C body: the manager's callback pointers are relocatable C
 * references. Thread entry, attribute objects, logging, and exact placement
 * must be qualified before selection into the firmware build. */
#include <stdint.h>
#include "display_driver_attributes.h"

struct display_driver_manager {
    void (*thread_init)(void);
    void (*queue_init)(void);
    void *thread;
    void *queue;
};
_Static_assert(sizeof(struct display_driver_manager)==16u,"display driver manager ABI");

extern void audio_display_driver_thread_entry(void *);
extern void *audio_thread_new(void (*)(void *),void *,const void *);
extern void *audio_queue_new(uint32_t,uint32_t,const void *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

void audio_display_driver_thread_init(void);
void audio_display_driver_queue_init(void);
struct display_driver_manager audio_display_driver_manager = {
    audio_display_driver_thread_init,audio_display_driver_queue_init,0,0,
};

static const char module[]="task.displaydrvmgr";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\display_mgr\\displaydrv_manager.c";
static const char thread_function[]="Disp_ThreadInit";
static const char queue_function[]="DISP_MessageQueueInit";
static const char thread_fail[]="[DISP_ThreadInit]osThreadNew fail";
static const char thread_fail_short[]="[task.displaydrvmgr][DISP_ThreadInit]osThreadNew fail";
static const char thread_ok[]="[DISP_ThreadInit]osThreadNew:0x%x, success";
static const char thread_ok_short[]="[task.displaydrvmgr][DISP_ThreadInit]osThreadNew:0x%x, success";
static const char queue_fail[]="[DISP_MessageQueueInit]osMessageQueueNew fail";
static const char queue_fail_short[]="[task.displaydrvmgr][DISP_MessageQueueInit]osMessageQueueNew fail";
static const char queue_ok[]="[DISP_MessageQueueInit]osMessageQueueNew:0x%x, success";
static const char queue_ok_short[]="[task.displaydrvmgr][DISP_MessageQueueInit]osMessageQueueNew:0x%x, success";

void audio_display_driver_thread_init(void) {
    audio_display_driver_manager.thread=audio_thread_new(audio_display_driver_thread_entry,0,
                                                        &audio_display_driver_thread_attrs);
    if(audio_display_driver_manager.thread==0) {
        if(audio_log_flags()&2u)
            audio_log_extended(1u,module,source,thread_function,0x64u,thread_fail);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x04000000u,thread_fail_short,thread_fail_short);
    } else {
        if(audio_log_flags()&2u)
            audio_log_extended(4u,module,source,thread_function,0x66u,thread_ok,
                               audio_display_driver_manager.thread);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x10400000u,thread_ok_short,thread_ok_short,
                                        audio_display_driver_manager.thread);
    }
}

void audio_display_driver_queue_init(void) {
    audio_display_driver_manager.queue=audio_queue_new(0x60u,0x24u,
                                                      &audio_display_driver_queue_attrs);
    if(audio_display_driver_manager.queue==0) {
        if(audio_log_flags()&2u)
            audio_log_extended(1u,module,source,queue_function,0x6eu,queue_fail);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x04000000u,queue_fail_short,queue_fail_short);
    } else {
        if(audio_log_flags()&2u)
            audio_log_extended(4u,module,source,queue_function,0x70u,queue_ok,
                               audio_display_driver_manager.queue);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x10400000u,queue_ok_short,queue_ok_short,
                                        audio_display_driver_manager.queue);
    }
}
