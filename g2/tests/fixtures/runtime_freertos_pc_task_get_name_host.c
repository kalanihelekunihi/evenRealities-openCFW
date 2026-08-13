#include <stddef.h>
#include <stdint.h>
#include <string.h>

static unsigned char open_cfw_test_explicit_tcb[0x70];
static unsigned char open_cfw_test_current_tcb_storage[0x70];
static void *open_cfw_test_current_tcb;
static uint32_t open_cfw_test_mask_calls;

#define OPEN_CFW_FREERTOS_PC_TASK_GET_NAME_CURRENT_TCB \
    open_cfw_test_current_tcb
#include "../../components/apollo_main/core_overlay/runtime_freertos_pc_task_get_name.c"

open_cfw_freertos_pc_task_get_name_u32 ulSetInterruptMask(void)
{
    open_cfw_test_mask_calls++;
    return 0U;
}

static void open_cfw_test_install_name(
    unsigned char *tcb,
    const char *name)
{
    size_t length = strlen(name);

    memset(tcb, 0, 0x70);
    if (length > 31U)
    {
        length = 31U;
    }
    memcpy(tcb + 0x34, name, length);
    tcb[0x34 + length] = '\0';
}

void open_cfw_test_pc_task_get_name_reset(
    const char *explicit_name,
    const char *current_name)
{
    open_cfw_test_install_name(open_cfw_test_explicit_tcb, explicit_name);
    open_cfw_test_install_name(
        open_cfw_test_current_tcb_storage,
        current_name);
    open_cfw_test_current_tcb = open_cfw_test_current_tcb_storage;
    open_cfw_test_mask_calls = 0U;
}

const char *open_cfw_test_pc_task_get_name_explicit(void)
{
    return open_cfw_freertos_pc_task_get_name(open_cfw_test_explicit_tcb);
}

const char *open_cfw_test_pc_task_get_name_current(void)
{
    return open_cfw_freertos_pc_task_get_name((void *)0);
}

uintptr_t open_cfw_test_pc_task_get_name_explicit_delta(void)
{
    return (uintptr_t)open_cfw_freertos_pc_task_get_name(
        open_cfw_test_explicit_tcb) -
        (uintptr_t)open_cfw_test_explicit_tcb;
}

uint32_t open_cfw_test_pc_task_get_name_mask_calls(void)
{
    return open_cfw_test_mask_calls;
}
