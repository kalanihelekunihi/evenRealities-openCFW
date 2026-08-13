#include <stdint.h>

static uint32_t test_irq;
static uint32_t test_set_result;
static uint32_t test_get_result;
static uint32_t test_clear_result;
static uint32_t test_wait_result;
static int32_t test_isr_result;
static int32_t test_yield;
static uint32_t test_calls[8];
static uintptr_t test_group;
static uint32_t test_bits;
static int32_t test_clear_on_exit;
static int32_t test_wait_all;
static uint32_t test_timeout;
static uint32_t test_pendsv;

uint32_t open_cfw_cmsis_irq_context(void) { return test_irq; }
void *open_cfw_rtos_event_group_static_create(void *buffer)
{ test_calls[0]++; test_group = (uintptr_t)buffer; return buffer; }
void *open_cfw_rtos_event_group_dynamic_create(void)
{ test_calls[1]++; return (void *)(uintptr_t)0x2468U; }
uint32_t open_cfw_rtos_event_group_set(void *group, uint32_t bits)
{ test_calls[2]++; test_group=(uintptr_t)group; test_bits=bits; return test_set_result; }
int32_t open_cfw_rtos_event_group_set_from_isr(void *group, uint32_t bits, int32_t *yield)
{ test_calls[3]++; test_group=(uintptr_t)group; test_bits=bits; *yield=test_yield; return test_isr_result; }
uint32_t open_cfw_rtos_event_group_get_bits_from_isr(void *group)
{ test_calls[4]++; test_group=(uintptr_t)group; return test_get_result; }
uint32_t open_cfw_rtos_event_group_clear(void *group, uint32_t bits)
{ test_calls[5]++; test_group=(uintptr_t)group; test_bits=bits; return test_clear_result; }
int32_t open_cfw_rtos_event_group_clear_from_isr(void *group, uint32_t bits)
{ test_calls[6]++; test_group=(uintptr_t)group; test_bits=bits; return test_isr_result; }
uint32_t open_cfw_rtos_event_group_wait(void *group, uint32_t bits, int32_t clear_on_exit, int32_t wait_all, uint32_t timeout)
{ test_calls[7]++; test_group=(uintptr_t)group; test_bits=bits; test_clear_on_exit=clear_on_exit; test_wait_all=wait_all; test_timeout=timeout; return test_wait_result; }

#define OPEN_CFW_CMSIS_EVENT_PENDSV_SET() (test_pendsv++)
#include "../../components/apollo_main/core_overlay/runtime_cmsis_event_flags.c"

void open_cfw_test_event_reset(uint32_t irq, int32_t isr_result, int32_t yield, uint32_t set_result, uint32_t get_result, uint32_t clear_result, uint32_t wait_result)
{
    unsigned i;
    test_irq=irq; test_isr_result=isr_result; test_yield=yield;
    test_set_result=set_result; test_get_result=get_result;
    test_clear_result=clear_result; test_wait_result=wait_result;
    for (i=0;i<8;i++) test_calls[i]=0;
    test_group=0; test_bits=0; test_clear_on_exit=-1; test_wait_all=-1;
    test_timeout=0; test_pendsv=0;
}
void *open_cfw_test_event_new(uintptr_t cb, uint32_t size, uint32_t mode)
{
    open_cfw_cmsis_event_attr attr = {0,0,(void *)cb,size};
    return open_cfw_cmsis_event_flags_new(mode ? &attr : 0);
}
uint32_t open_cfw_test_event_call(unsigned i) { return test_calls[i]; }
uintptr_t open_cfw_test_event_group(void) { return test_group; }
uint32_t open_cfw_test_event_bits(void) { return test_bits; }
int32_t open_cfw_test_event_clear_on_exit(void) { return test_clear_on_exit; }
int32_t open_cfw_test_event_wait_all(void) { return test_wait_all; }
uint32_t open_cfw_test_event_timeout(void) { return test_timeout; }
uint32_t open_cfw_test_event_pendsv(void) { return test_pendsv; }
