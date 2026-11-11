#include <stdint.h>
#include <stddef.h>

struct r1_event_context {void (*create)(void),(*stop)(void);void *thread,*queue;};
extern struct r1_event_context r1_event_system;
_Static_assert(offsetof(struct r1_event_context,thread)==8,"stock thread reference cell");
volatile uint32_t r1_health_activity_enable_words[2]
    __attribute__((section(".r1.health.activity.enable_words"),aligned(4)))={0};
extern uint32_t r1_kv_dev_info_flag_word_get(void *,void *);
extern uint32_t r1_gomore_authorization_dispatch_native(uint32_t,uint32_t);
extern uint32_t r1_subscriber_register(uint32_t,uint32_t,uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);

__attribute__((noinline,section(".text.r1_cfg_byte_get_73798")))
uint32_t r1_cfg_byte_get_73798(void)
{
    /* Stock initializes only the byte it later reads. The NV helper can
     * write more of the word, but the remaining bytes are never observed. */
    uint32_t value=0;
    (void)r1_kv_dev_info_flag_word_get(&value,NULL);
    return (uint8_t)value;
}

__attribute__((section(".text.r1_health_activity_mode_callback")))
void r1_health_activity_mode_callback(const volatile void *status)
{
    (void)status;
}

__attribute__((section(".text.r1_native_health_activity_enable")))
uint32_t r1_native_health_activity_enable(void)
{
    r1_health_activity_enable_words[0]=0;
    r1_health_activity_enable_words[1]=0;
    if (r1_cfg_byte_get_73798()) {
        if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
            (void)r1_structured_log_format(0x0c000000,
                "[RING]health enabled, enable activity module",
                "[RING]health enabled, enable activity module");
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_0(0x001c0003,"health enabled, enable activity module");
        (void)r1_gomore_authorization_dispatch_native(0,1);
    }
    return r1_subscriber_register(4,(uint32_t)(uintptr_t)r1_health_activity_mode_callback,
        (uint32_t)(uintptr_t)&r1_event_system.thread);
}
