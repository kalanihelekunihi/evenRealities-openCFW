/* Display thread startup, native 0x444720. The queue and task attributes
 * come from authenticated ROM templates at 0x776994 and 0x75378c. */
#include <stdint.h>

extern const uint32_t g2_display_state_table[]; /* ROM0x776a3c, selected by 0x47394c */
extern uint8_t g2_display_queue_control[0x50]; /* RAM0x200729e8 */
extern uint8_t g2_display_queue_storage[0x480]; /* RAM0x203780c0 */
extern uint32_t g2_display_state_cell; /* RAM0x200744cc */
extern void *g2_display_queue; /* RAM0x200744e4 */
extern void *g2_display_sender_mutex; /* RAM0x200744e8 */
extern uint32_t g2_display_ring[5]; /* RAM0x20073b60 */
extern uint8_t g2_display_ring_storage[0xa000]; /* RAM0x200e99b4 */
extern void audio_uart_display_setup0(void); /* 0x444694 */
extern void audio_uart_display_setup1(void); /* 0x4446b4 */
extern void audio_uart_display_thread(void *); /* 0x4437e0 */
extern void *audio_queue_new(uint32_t,uint32_t,const void *); /* 0x449a32 */
extern void *audio_uart_mutex_new(uint32_t); /* 0x44971c */
extern void *audio_thread_new(void (*)(void *),void *,const void *); /* 0x4490e2 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="display_thread";
static const char source_file[]=
 "D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\display_thread.c";
static const char function_name[]="ui_display_thread_startup";
static const char queue_message[]="dispThread_xQueue1 create failed..";
static const char queue_short[]="[display_thread]dispThread_xQueue1 create failed..";
static const char mutex_message[]="Failed to create uart sender mutex";
static const char mutex_short[]="[display_thread]Failed to create uart sender mutex";
static const char queue_name[]="DispQueue";
static const char task_name[]="ui_task";

typedef struct {const char *name;uint32_t bits;void *control;uint32_t control_size;
                void *storage;uint32_t storage_size;} queue_attr;
typedef struct {const char *name;uint32_t bits;void *control;uint32_t control_size;
                void *stack;uint32_t stack_size;uint32_t priority;
                uint32_t tz;uint32_t reserved;} task_attr;

static void startup_failure(uint32_t line,const char *message,
                            const char *short_message,uint8_t level) {
    if(audio_log_flags()&2u)
        audio_log_extended(level,module,source_file,function_name,line,message);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output((uint32_t)level<<26,short_message,
                                    short_message);
}

uint32_t audio_uart_service_prepare0(void) {
    g2_display_state_cell=(uint32_t)(uintptr_t)g2_display_state_table;
    audio_uart_display_setup0();
    audio_uart_display_setup1();
    queue_attr qa={queue_name,0u,g2_display_queue_control,0x50u,
                   g2_display_queue_storage,0x480u};
    g2_display_queue=audio_queue_new(0x60u,0xcu,&qa);
    if(g2_display_queue==0) {
        startup_failure(0x43eu,queue_message,queue_short,2u);
        return UINT32_MAX;
    }
    g2_display_ring[4]=0u;
    g2_display_ring[1]=0xa000u;
    g2_display_ring[0]=(uint32_t)(uintptr_t)g2_display_ring_storage;
    g2_display_ring[3]=0u;
    g2_display_ring[2]=0u;
    g2_display_sender_mutex=audio_uart_mutex_new(0u);
    if(g2_display_sender_mutex==0) {
        startup_failure(0x44au,mutex_message,mutex_short,1u);
        return UINT32_MAX;
    }
    task_attr ta={task_name,0u,0,0u,0,0xc000u,0x2cu,0u,0u};
    (void)audio_thread_new(audio_uart_display_thread,0,&ta);
    return 0u;
}
