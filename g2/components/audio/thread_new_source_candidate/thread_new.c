/* Experimental CMSIS osThreadNew outer body, Apollo stock 0x4490e2.
 * Static/dynamic FreeRTOS task allocation remain typed lower calls. */
#include <stdint.h>
#include <stddef.h>
typedef void (*thread_entry)(void *);
typedef struct {
    const char *name;                 /* +0 */
    uint32_t attr_bits;               /* +4 */
    void *cb_mem;                     /* +8 */
    uint32_t cb_size;                 /* +12 */
    void *stack_mem;                  /* +16 */
    uint32_t stack_size;              /* +20, bytes */
    uint32_t priority;                /* +24 */
    uint32_t tz_module;               /* +28 */
    uint32_t reserved;                /* +32 */
} thread_attrs;
_Static_assert(offsetof(thread_attrs,priority)==24 &&
               sizeof(thread_attrs)==36,"stock CMSIS thread attr prefix");
extern uint32_t audio_irq_context(void);
extern void *audio_daemon_create_static(thread_entry,const char *,uint32_t,
                                         void *,uint32_t,void *,void *);
extern int32_t g2_thread_create_dynamic(thread_entry,const char *,uint16_t,
                                         void *,uint32_t,void **);

void *osThreadNew(thread_entry entry,void *argument,const thread_attrs *a) {
    void *created=0;
    if(audio_irq_context()!=0u || !entry) return 0;
    const char *name=0;
    uint32_t depth=1024u,priority=24u;
    int mode=0;
    if(a) {
        name=a->name;
        if(a->priority!=0u) priority=a->priority;
        if(priority==0u || priority>56u || (a->attr_bits&1u)) return 0;
        if(a->stack_size!=0u) depth=a->stack_size>>2;
        if(a->cb_mem && a->cb_size>=0x70u && a->stack_mem && a->stack_size)
            mode=1;
        else if(a->cb_mem || a->cb_size || a->stack_mem) mode=-1;
    }
    if(mode==1)
        return audio_daemon_create_static(entry,name,depth,argument,priority,
                                          a->stack_mem,a->cb_mem);
    if(mode==0 && g2_thread_create_dynamic(entry,name,(uint16_t)depth,
                                            argument,priority,&created)!=1)
        created=0;
    return created;
}
void *audio_thread_new(thread_entry,void *,const thread_attrs *)
    __attribute__((alias("osThreadNew")));
