/* init_thread_pool, native 0x49137a. ROM queue/thread attributes and RAM
 * pool extents are product-owned data contracts, with no default values. */
#include <stdint.h>
extern void *audio_uart_mutex_new(const void *);
extern int32_t audio_uart_mutex_delete(void *); /* osMutexDelete 0x44986e */
extern void *audio_queue_new(uint32_t,uint32_t,const void *);
extern int32_t audio_queue_delete(void *);
extern void *audio_thread_new(void (*)(void *),void *,const void *);
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);
extern int32_t g2_audio_dump_snprintf(char *,uint32_t,const char *,...); /* 0x44b728 */
extern void audio_uart_worker_thread(void *); /* 0x49110c */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern uint8_t audio_uart_pool_initialized; /* RAM0x20075031 */
extern void *audio_uart_pool_mutex; /* RAM0x20074aa4 */
extern void *audio_uart_pool_queue; /* RAM0x20074aa0 */
extern void *audio_uart_pool_threads[8]; /* RAM0x200739dc */
extern char audio_uart_pool_names[8][20]; /* RAM0x20071710 */
extern uint8_t audio_uart_pool_stacks[8][0x1000]; /* RAM0x20033558 */
extern uint8_t audio_uart_pool_controls[8][0x70]; /* RAM0x2006d0bc */
struct pool_queue_attrs {
    const char *name; uint32_t attr_bits; void *cb_mem; uint32_t cb_size;
    void *mq_mem; uint32_t mq_size;
};
struct pool_thread_attrs {
    const char *name; uint32_t attr_bits; void *cb_mem; uint32_t cb_size;
    void *stack_mem; uint32_t stack_size; uint32_t priority;
    uint32_t tz_module; uint32_t reserved;
};
_Static_assert(sizeof(struct pool_queue_attrs)==24u,"queue attributes ABI");
_Static_assert(sizeof(struct pool_thread_attrs)==36u,"thread attributes ABI");
extern const struct pool_queue_attrs audio_uart_pool_queue_attrs; /* native 0x77ccac */
extern const struct pool_thread_attrs audio_uart_pool_thread_attrs; /* native 0x75bd00 */

static const char module[]="thread_pool";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\thread_pool.c";
static const char fn[]="init_thread_pool";
static const char name_format[]="worker_thread_%d";
static const char e_already[]="init_thread_pool: thread pool already initialized";
static const char c_already[]="[thread_pool]init_thread_pool: thread pool already initialized";
static const char e_mutex[]="init_thread_pool: failed to create mutex";
static const char c_mutex[]="[thread_pool]init_thread_pool: failed to create mutex";
static const char e_queue[]="init_thread_pool: failed to create message queue";
static const char c_queue[]="[thread_pool]init_thread_pool: failed to create message queue";
static const char e_thread[]="init_thread_pool: failed to create worker thread %d";
static const char c_thread[]="[thread_pool]init_thread_pool: failed to create worker thread %d";
static const char e_none[]="init_thread_pool: failed to create any worker threads";
static const char c_none[]="[thread_pool]init_thread_pool: failed to create any worker threads";
static const char e_ok[]="Thread pool initialized successfully with %d threads";
static const char c_ok[]="[thread_pool]Thread pool initialized successfully with %d threads";

static void log0(uint8_t level,uint32_t line,const char *e,const char *c) {
    if(audio_log_flags()&2u)
        audio_log_extended(level,module,source,fn,line,e);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output((uint32_t)level<<26,c,c);
}
static void log1(uint8_t level,uint32_t line,const char *e,const char *c,
                 uint32_t n) {
    if(audio_log_flags()&2u)
        audio_log_extended(level,module,source,fn,line,e,n);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(((uint32_t)level<<26)|0x400000u,c,c,n);
}

uint32_t audio_uart_poll_thread_start(void) {
    if(audio_uart_pool_initialized!=0u) {
        log0(2u,0x79u,e_already,c_already);
        return UINT32_MAX;
    }
    audio_uart_pool_mutex=audio_uart_mutex_new(0);
    if(audio_uart_pool_mutex==0) {
        log0(1u,0x80u,e_mutex,c_mutex);
        return UINT32_MAX;
    }
    uint8_t queue_attrs[24];
    (void)audio_queue_copy_bytes(queue_attrs,&audio_uart_pool_queue_attrs,24u);
    audio_uart_pool_queue=audio_queue_new(0x96u,0x14u,queue_attrs);
    if(audio_uart_pool_queue==0) {
        log0(1u,0x8fu,e_queue,c_queue);
        (void)audio_uart_mutex_delete(audio_uart_pool_mutex);
        audio_uart_pool_mutex=0;
        return UINT32_MAX;
    }
    uint32_t count=0u;
    for(uint32_t i=0u;i<8u;++i) {
        uint32_t attrs[9];
        (void)audio_queue_copy_bytes(attrs,&audio_uart_pool_thread_attrs,36u);
        char name[20]={0};
        (void)g2_audio_dump_snprintf(name,20u,name_format,i);
        for(uint32_t k=0u;k<20u;++k) {
            audio_uart_pool_names[i][k]=name[k];
            if(name[k]==0) break;
        }
        attrs[0]=(uint32_t)(uintptr_t)audio_uart_pool_names[i];
        attrs[2]=(uint32_t)(uintptr_t)audio_uart_pool_controls[i];
        attrs[3]=0x70u;
        attrs[4]=(uint32_t)(uintptr_t)audio_uart_pool_stacks[i];
        attrs[5]=0x1000u;
        audio_uart_pool_threads[i]=audio_thread_new(audio_uart_worker_thread,0,
                                                     attrs);
        if(audio_uart_pool_threads[i]==0)
            log1(1u,0xa6u,e_thread,c_thread,i);
        else ++count;
    }
    if(count==0u) {
        log0(1u,0xb4u,e_none,c_none);
        (void)audio_queue_delete(audio_uart_pool_queue);
        audio_uart_pool_queue=0;
        (void)audio_uart_mutex_delete(audio_uart_pool_mutex);
        audio_uart_pool_mutex=0;
        return UINT32_MAX;
    }
    audio_uart_pool_initialized=1u;
    log1(3u,0xb0u,e_ok,c_ok,count);
    return 0u;
}
