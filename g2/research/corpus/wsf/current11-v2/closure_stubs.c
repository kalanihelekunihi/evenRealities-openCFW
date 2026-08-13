#include "runtime_cordio_wsf_timer_candidate.h"
struct open_cfw_cordio_wsf_timer_queue open_cfw_cordio_wsf_timer_queue_candidate;
void *open_cfw_cordio_wsf_freertos_timer_candidate;
uint32_t open_cfw_cordio_wsf_last_tick_candidate;
static struct open_cfw_cordio_wsf_timer closure_timer;
void open_cfw_cordio_wsf_task_lock_candidate(void) {}
void open_cfw_cordio_wsf_task_unlock_candidate(void) {}
void open_cfw_cordio_wsf_queue_remove_candidate(
    struct open_cfw_cordio_wsf_timer_queue *q,
    struct open_cfw_cordio_wsf_timer *t,
    struct open_cfw_cordio_wsf_timer *p
) { (void)q; (void)t; (void)p; }
void open_cfw_cordio_wsf_queue_insert_candidate(
    struct open_cfw_cordio_wsf_timer_queue *q,
    struct open_cfw_cordio_wsf_timer *t,
    struct open_cfw_cordio_wsf_timer *p
) { (void)q; (void)t; (void)p; }
void open_cfw_cordio_wsf_task_set_ready_candidate(uint8_t h, uint8_t e) { (void)h; (void)e; }
uint32_t open_cfw_cordio_wsf_tick_counter_get_candidate(void) { return 0U; }
void *open_cfw_cordio_wsf_timer_create_candidate(
    const char *name, uint32_t period, bool reload, void *id,
    void (*callback)(void *)
) { (void)name; (void)period; (void)reload; (void)id; (void)callback; return (void *)1; }
int open_cfw_cordio_wsf_timer_command_candidate(
    void *timer, uint32_t command, uint32_t value,
    uint32_t reserved, uint32_t wait_ticks
) { (void)timer; (void)command; (void)value; (void)reserved; (void)wait_ticks; return 1; }
void open_cfw_cordio_wsf_timer_command_failure_candidate(void) {}
void open_cfw_cordio_wsf_timer_fatal_candidate(void) {}
void open_cfw_current11_closure_root(void) {
    bool running;
    open_cfw_cordio_wsf_timer_remove_candidate(&closure_timer);
    open_cfw_cordio_wsf_timer_insert_candidate(&closure_timer, 1U);
    open_cfw_cordio_wsf_timer_callback_candidate(0);
    open_cfw_cordio_wsf_timer_init_candidate();
    open_cfw_cordio_wsf_timer_start_sec_candidate(&closure_timer, 1U);
    open_cfw_cordio_wsf_timer_start_ms_candidate(&closure_timer, 10U);
    open_cfw_cordio_wsf_timer_stop_candidate(&closure_timer);
    open_cfw_cordio_wsf_timer_update_candidate(1U);
    (void)open_cfw_cordio_wsf_timer_next_expiration_candidate(&running);
    (void)open_cfw_cordio_wsf_timer_service_expired_candidate(0U);
    open_cfw_cordio_wsf_timer_update_ticks_candidate();
}
