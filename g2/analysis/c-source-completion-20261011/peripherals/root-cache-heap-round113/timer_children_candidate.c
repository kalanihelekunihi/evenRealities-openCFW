/* Native LVGL list/tick/lock/wait leaves for 0x464344. */
#include <stdint.h>
extern uint8_t audio_uart_lv_tick_state[]; /* RAM0x2006f600 */
extern uint8_t audio_uart_lv_lock_cell[]; /* RAM0x2006f718 */
extern uint8_t audio_uart_display_lv_state[]; /* RAM0x2006f548 */
extern int32_t xQueueTakeMutexRecursive(void *,uint32_t);
extern int32_t xQueueGiveMutexRecursive(void *);
extern void *audio_uart_mutex_dynamic_create(uint32_t); /* 0x4416d6 */
extern void stock_enter_critical(void); /* 0x4420d0 */
extern void stock_exit_critical(void); /* 0x4420e8 */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,
                                 const char *,const char *,...); /* 0x44d25c */
void audio_uart_lv_list_remove(void *,void *); /* 0x482c0e */
extern uint8_t audio_uart_lv_heap_pool[]; /* RAM0x20000338, DAT_0048436c */
extern int32_t xQueueSemaphoreTake(void *,uint32_t); /* selected native 0x441c44 */
extern int32_t audio_uart_queue_send(void *,const void *,uint32_t,uint32_t); /* selected 0x4417ee */
extern uint32_t g2_tlsf_block_size(void *); /* selected 0x4cfd70 */
extern void g2_file_pool_free(void *,void *); /* selected 0x4d0808 */
extern uint8_t audio_uart_lv_static_slot[]; /* RAM0x2006f5ac, DAT_0044f7a4 */
extern void audio_uart_lv_assert_null(void); /* native 0x464512 logging/fault */
void audio_uart_lv_timer_delete(void *);
void audio_uart_lv_timer_pause(void *);
void audio_uart_lv_free(void *);
void audio_uart_lv_heap_free(void *);
uint32_t audio_uart_lv_lock_core(void *);
uint32_t audio_uart_lv_unlock_core(void *);

/* Native recursive LVGL mutex at 0x4d477a/0x4d47cc/0x4d4666/0x4d4696. */
static void audio_uart_lv_mutex_init(uint32_t *cell) {
    cell[1]=(uint32_t)(uintptr_t)audio_uart_mutex_dynamic_create(4u);
    if(cell[1]==0u)
        audio_uart_lvgl_log(3u,"lv_freertos.c",0x1bau,
                            "prvMutexInit","xSemaphoreCreateMutex failed!");
    else cell[0]=1u;
}
void audio_uart_lv_mutex_ensure(uint32_t *cell) {
    if(cell[0]==0u) {
        stock_enter_critical();
        if(cell[0]==0u) audio_uart_lv_mutex_init(cell);
        stock_exit_critical();
    }
}
uint32_t audio_uart_lv_lock_core(void *cell) {
    uint32_t *mutex=(uint32_t *)cell;
    audio_uart_lv_mutex_ensure(mutex);
    uint32_t ok=(uint32_t)xQueueTakeMutexRecursive((void *)(uintptr_t)mutex[1],UINT32_MAX);
    if(ok!=1u)
        audio_uart_lvgl_log(3u,"lv_freertos.c",0x84u,
                            "lv_mutex_lock","xSemaphoreTake failed!");
    return ok==1u;
}
uint32_t audio_uart_lv_unlock_core(void *cell) {
    uint32_t *mutex=(uint32_t *)cell;
    audio_uart_lv_mutex_ensure(mutex);
    uint32_t ok=(uint32_t)xQueueGiveMutexRecursive((void *)(uintptr_t)mutex[1]);
    if(ok!=1u)
        audio_uart_lvgl_log(3u,"lv_freertos.c",0xa8u,
                            "lv_mutex_unlock","xSemaphoreGive failed!");
    return ok==1u;
}

void *audio_uart_lv_list_first(void *list) {
    if(list==0) return 0;
    return (void *)(uintptr_t)*(uint32_t *)(void *)((uint8_t *)list+4u);
}
void *audio_uart_lv_list_next(void *list,void *node) {
    uintptr_t base=*(uint32_t *)(void *)list;
    uintptr_t offset=(uintptr_t)node;
    return (void *)(uintptr_t)*(uint32_t *)(void *)(base+offset+4u);
}
uint32_t audio_uart_lv_tick(void) {
    uint8_t *state=audio_uart_lv_tick_state;
    uint32_t callback=*(uint32_t *)(void *)(state+8u);
    if(callback!=0u)
        return ((uint32_t (*)(void))(uintptr_t)callback)();
    state[4u]=1u;
    return *(uint32_t *)(void *)state;
}
uint32_t audio_uart_lv_elapsed(uint32_t start) {
    return audio_uart_lv_tick()-start;
}
uint32_t audio_uart_lv_timer_remaining(void *timer) {
    uint32_t period=*(const uint32_t *)(const void *)timer;
    uint32_t baseline=*(const uint32_t *)(const void *)((const uint8_t *)timer+4u);
    uint32_t elapsed=audio_uart_lv_elapsed(baseline);
    return elapsed<period?period-elapsed:0u;
}
void audio_uart_lv_lock(void) {
    (void)audio_uart_lv_lock_core(audio_uart_lv_lock_cell);
}
void audio_uart_lv_unlock(void) {
    (void)audio_uart_lv_unlock_core(audio_uart_lv_lock_cell);
}
static uint32_t lv_node_prev(uint32_t *list,uint32_t node) {
    return *(uint32_t *)(uintptr_t)(list[0]+node);
}
static uint32_t lv_node_next(uint32_t *list,uint32_t node) {
    return *(uint32_t *)(uintptr_t)(list[0]+node+4u);
}
static void lv_set_prev(uint32_t *list,uint32_t node,uint32_t previous) {
    if(node!=0u) *(uint32_t *)(uintptr_t)(list[0]+node)=previous;
}
static void lv_set_next(uint32_t *list,uint32_t node,uint32_t next) {
    if(node!=0u) *(uint32_t *)(uintptr_t)(list[0]+node+4u)=next;
}
void audio_uart_lv_list_remove(void *list,void *node) {
    if(list==0) return;
    uint32_t *l=(uint32_t *)list;
    uint32_t n=(uint32_t)(uintptr_t)node;
    if(l[1]==n) {
        l[1]=lv_node_next(l,n);
        if(l[1]==0u) l[2]=0u;
        else lv_set_prev(l,l[1],0u);
    } else if(l[2]==n) {
        l[2]=lv_node_prev(l,n);
        if(l[2]==0u) l[1]=0u;
        else lv_set_next(l,l[2],0u);
    } else {
        uint32_t previous=lv_node_prev(l,n);
        uint32_t next=lv_node_next(l,n);
        lv_set_next(l,previous,next);
        lv_set_prev(l,next,previous);
    }
}
uint32_t audio_uart_lv_timer_execute(void *timer) {
    uint8_t *t=(uint8_t *)timer;
    if((t[0x14u]&1u)!=0u) return 0u;
    uint32_t ran=0u;
    if(audio_uart_lv_timer_remaining(timer)==0u) {
        int32_t count=*(int32_t *)(void *)(t+0x10u);
        if(count>0) *(int32_t *)(void *)(t+0x10u)=count-1;
        *(uint32_t *)(void *)(t+4u)=audio_uart_lv_tick();
        uint32_t callback=*(uint32_t *)(void *)(t+8u);
        if(callback!=0u&&count!=0)
            ((void (*)(void *))(uintptr_t)callback)(timer);
        ran=1u;
    }
    if(audio_uart_display_lv_state[0x82u]==0u &&
       *(int32_t *)(void *)(t+0x10u)==0) {
        if((t[0x14u]&2u)!=0u) audio_uart_lv_timer_delete(timer);
        else audio_uart_lv_timer_pause(timer);
    }
    return ran;
}
void audio_uart_lv_timer_delete(void *timer) {
    audio_uart_lv_list_remove(audio_uart_display_lv_state+0x74u,timer);
    audio_uart_display_lv_state[0x82u]=1u;
    audio_uart_lv_free(timer);
}
void audio_uart_lv_timer_pause(void *timer) {
    if(timer==0) audio_uart_lv_assert_null();
    else *(uint32_t *)(void *)((uint8_t *)timer+0x14u)|=1u;
}
void audio_uart_lv_free(void *pointer) {
    if(pointer!=0&&pointer!=audio_uart_lv_static_slot)
        audio_uart_lv_heap_free(pointer);
}
