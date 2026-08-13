#include <stdint.h>
#include <stdlib.h>

static uint32_t test_irq;
static int test_malloc_fail;
static int test_create_fail;
static uint32_t test_malloc_calls, test_free_calls, test_static_calls, test_dynamic_calls, test_callback_calls;
static uintptr_t test_freed, test_buffer, test_context, test_callback, test_name, test_argument;
static uint32_t test_period, test_reload;
static void *test_timer_context;

uint32_t open_cfw_cmsis_irq_context(void) { return test_irq; }
void *open_cfw_freertos_heap4_malloc(uint32_t size)
{ (void)size; test_malloc_calls++; return test_malloc_fail ? 0 : malloc(16U); }
void open_cfw_freertos_heap4_free(void *memory)
{ test_free_calls++; test_freed=(uintptr_t)memory; free(memory); }
void *open_cfw_rtos_timer_static_create(const char *name,uint32_t period,uint32_t reload,void *context,void (*callback)(void *),void *buffer)
{ test_static_calls++; test_name=(uintptr_t)name; test_period=period; test_reload=reload; test_context=(uintptr_t)context; test_callback=(uintptr_t)callback; test_buffer=(uintptr_t)buffer; return test_create_fail?0:(void *)0x1110; }
void *open_cfw_rtos_timer_dynamic_create(const char *name,uint32_t period,uint32_t reload,void *context,void (*callback)(void *))
{ test_dynamic_calls++; test_name=(uintptr_t)name; test_period=period; test_reload=reload; test_context=(uintptr_t)context; test_callback=(uintptr_t)callback; return test_create_fail?0:(void *)0x2220; }
void *open_cfw_rtos_timer_get_context(const void *timer)
{ (void)timer; return test_timer_context; }

#include "../../components/apollo_main/core_overlay/runtime_cmsis_timer_new.c"

static void test_application_callback(void *argument)
{ test_callback_calls++; test_argument=(uintptr_t)argument; }

void open_cfw_test_timer_new_reset(uint32_t irq,int malloc_fail,int create_fail)
{ test_irq=irq;test_malloc_fail=malloc_fail;test_create_fail=create_fail;test_malloc_calls=0;test_free_calls=0;test_static_calls=0;test_dynamic_calls=0;test_callback_calls=0;test_freed=0;test_buffer=0;test_context=0;test_callback=0;test_name=0;test_argument=0;test_period=0;test_reload=0;test_timer_context=0; }
void *open_cfw_test_timer_new_call(uint32_t type,uintptr_t argument,uintptr_t name,uintptr_t cb,uint32_t size,uint32_t mode)
{ open_cfw_cmsis_timer_new_attr attr={(const char *)name,0,(void *)cb,size}; return open_cfw_cmsis_timer_new(test_application_callback,type,(void *)argument,mode?&attr:0); }
void *open_cfw_test_timer_new_null_function(void)
{ return open_cfw_cmsis_timer_new(0,0,0,0); }
void open_cfw_test_timer_new_invoke(uintptr_t context)
{ test_timer_context=(void *)context; open_cfw_cmsis_timer_callback((void *)0x1110); }
#define GETTER(name,type) type open_cfw_test_timer_new_##name(void){return (type)test_##name;}
GETTER(malloc_calls,uint32_t) GETTER(free_calls,uint32_t) GETTER(static_calls,uint32_t) GETTER(dynamic_calls,uint32_t) GETTER(callback_calls,uint32_t)
GETTER(freed,uintptr_t) GETTER(buffer,uintptr_t) GETTER(context,uintptr_t) GETTER(callback,uintptr_t) GETTER(name,uintptr_t) GETTER(argument,uintptr_t)
GETTER(period,uint32_t) GETTER(reload,uint32_t)
