/* Native Main Thread_SendEvtToRingTask 0x4c543e, including all log branches. */
#include <stdint.h>
struct ring_thread_manager {uint8_t reserved[8];void *thread;};
_Static_assert(sizeof(struct ring_thread_manager)==12u,"ring thread ABI");
extern struct ring_thread_manager audio_uart_ring_thread_manager; /* live RAM 0x20004120 */
extern uint32_t audio_log_flags(void); /* selected 0x43d0ce */
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...); /* selected 0x43d574 */
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...); /* selected 0x43ce9e */
extern uint32_t audio_thread_flags_set(void *,uint32_t); /* selected 0x449238 */
static const char module[]="task.ring";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_ring.c";
static const char function[]="Thread_SendEvtToRingTask";
static const char message[]="Thread_SendEvtToRingTask = 0x%x";
static const char short_message[]="[task.ring]Thread_SendEvtToRingTask = 0x%x";
uint32_t Thread_SendEvtToRingTask(uint32_t flags) {
    uint32_t result=flags;
    if((audio_log_flags()&2u)!=0u) {
        audio_log_extended(4u,module,path,function,374u,message,flags);
        result=374u; /* native overwrites saved R0 stack slot with line number */
    }
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x10400000u,short_message,short_message,flags);
    (void)audio_thread_flags_set(audio_uart_ring_thread_manager.thread,flags);
    return result;
}
