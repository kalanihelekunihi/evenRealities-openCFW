/* Native FreeRTOS timer construction 0x47e6dc/0x47e712/0x47e75a and ID 0x47eb26. */
#include <stdint.h>
typedef struct {
    const char *name;             /* +0 */
    uint32_t list_item[5];        /* +4..+23, initialized by list helper */
    uint32_t period;              /* +24 */
    uintptr_t id;                 /* +28 */
    void (*callback)(void *);     /* +32 */
    uint8_t reserved[4];         /* +36..+39 */
    uint8_t flags;               /* +40 */
    uint8_t trailing[3];         /* +41..+43 */
} audio_timer_t;
_Static_assert(sizeof(audio_timer_t)==44u,"FreeRTOS native timer ABI");
extern void *pvPortMalloc(uint32_t);
extern void stock_enter_critical(void); /* selected 0x4420d0 */
extern void stock_exit_critical(void);  /* selected 0x4420e8 */
extern void audio_daemon_initialize_queue(void); /* selected native 0x47eab8 */
static void timer_setup(audio_timer_t *timer,const char *name,uint32_t period,
                        uint32_t auto_reload,uintptr_t id,void (*callback)(void *)) {
    audio_daemon_initialize_queue();
    timer->name=name;
    timer->period=period;
    timer->id=id;
    timer->callback=callback;
    timer->list_item[4]=0; /* native store at +20 */
    if(auto_reload!=0u) timer->flags|=4u;
}
void *audio_freertos_timer_create_dynamic(const char *name,uint32_t period,
                                          uint32_t auto_reload,uintptr_t id,
                                          void (*callback)(void *)) {
    audio_timer_t *timer=(audio_timer_t *)pvPortMalloc(44u);
    if(timer!=0) {
        timer->flags=0;
        timer_setup(timer,name,period,auto_reload,id,callback);
    }
    return timer;
}
void *audio_freertos_timer_create_static(const char *name,uint32_t period,
                                         uint32_t auto_reload,uintptr_t id,
                                         void (*callback)(void *),void *storage) {
    audio_timer_t *timer=(audio_timer_t *)storage;
    /* osTimerNew calls this only with a non-null, >=44-byte buffer. */
    timer->flags=2u;
    timer_setup(timer,name,period,auto_reload,id,callback);
    return timer;
}
uintptr_t audio_freertos_timer_get_id(void *handle) {
    audio_timer_t *timer=(audio_timer_t *)handle;
    stock_enter_critical();
    uintptr_t id=timer->id;
    stock_exit_critical();
    return id;
}
