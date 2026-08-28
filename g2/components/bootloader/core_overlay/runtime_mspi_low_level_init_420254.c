/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room reconstruction of the bounded G2 bootloader MX25U25643G
 * low-level MSPI initialization entry.
 */

typedef __UINT8_TYPE__ open_cfw_low_init_u8;
typedef __UINT32_TYPE__ open_cfw_low_init_u32;
typedef __UINTPTR_TYPE__ open_cfw_low_init_word;

enum {
    OPEN_CFW_LOW_INIT_STATE_ADDRESS = 0x20026FD0U,
    OPEN_CFW_LOW_INIT_HANDLE_ADDRESS = 0x200270DCU,
    OPEN_CFW_LOW_INIT_DEFAULT_CONFIG_ADDRESS = 0x20000224U,
    OPEN_CFW_LOW_INIT_TCB_ADDRESS = 0x200F4C00U,
    OPEN_CFW_LOW_INIT_TCB_WORDS = 256U,
    OPEN_CFW_LOW_INIT_DEVICE_CONFIG_OFFSET = 8U,
    OPEN_CFW_LOW_INIT_DEVICE_QUAD_CE0 = 16U,
    OPEN_CFW_LOW_INIT_CLOCK_PIN = 103U,
    OPEN_CFW_LOW_INIT_INTERRUPT_MASK = 0x1A80U,
    OPEN_CFW_LOW_INIT_MSPI1_IRQ = 21U,
    OPEN_CFW_LOW_INIT_IRQ_PRIORITY = 4U,
    OPEN_CFW_LOW_INIT_LOG_THUMB = 0x004176CFU,
    OPEN_CFW_LOW_INIT_LOG_TAG = 0x00433CD8U,
    OPEN_CFW_LOW_INIT_LOG_FILE = 0x00431540U,
    OPEN_CFW_LOW_INIT_LOG_FUNCTION = 0x00433180U,
    OPEN_CFW_LOW_INIT_POWER_FORMAT = 0x00432CC4U,
    OPEN_CFW_LOW_INIT_CONFIGURE_FORMAT = 0x00432CE8U,
    OPEN_CFW_LOW_INIT_DEVICE_FORMAT = 0x00432624U,
    OPEN_CFW_LOW_INIT_ENABLE_FORMAT = 0x004331A0U,
    OPEN_CFW_LOW_INIT_INTERRUPT_FORMAT = 0x00432A4CU,
    OPEN_CFW_LOW_INIT_SUCCESS_FORMAT = 0x00432A74U
};

typedef struct {
    open_cfw_low_init_u32 instance;
    open_cfw_low_init_u32 device_config;
    open_cfw_low_init_u32 handle_word;
    open_cfw_low_init_u8 initialized;
    open_cfw_low_init_u8 reserved[3];
} open_cfw_low_init_state;

typedef struct {
    open_cfw_low_init_u32 tcb_words;
    open_cfw_low_init_u32 tcb_address;
    open_cfw_low_init_u32 clock_on_deepsleep;
} open_cfw_low_init_controller_config;

typedef open_cfw_low_init_u32 (*open_cfw_low_init_initialize_fn)(
    open_cfw_low_init_u32, void **);
typedef open_cfw_low_init_u32 (*open_cfw_low_init_power_fn)(
    void *, open_cfw_low_init_u32, open_cfw_low_init_u32);
typedef open_cfw_low_init_u32 (*open_cfw_low_init_configure_fn)(
    void *, const void *);
typedef open_cfw_low_init_u32 (*open_cfw_low_init_handle_fn)(void *);
typedef open_cfw_low_init_u32 (*open_cfw_low_init_interrupt_fn)(
    void *, open_cfw_low_init_u32);
typedef open_cfw_low_init_u32 (*open_cfw_low_init_pin_get_fn)(
    open_cfw_low_init_u32, open_cfw_low_init_u32 *);
typedef open_cfw_low_init_u32 (*open_cfw_low_init_master_enable_fn)(void);
typedef void (*open_cfw_low_init_log_fn)(
    open_cfw_low_init_u32, const void *, const void *, const void *,
    open_cfw_low_init_u32, const void *, ...);

void open_cfw_bootloader_mspi_xip_config_41ff34(open_cfw_low_init_u32);
void open_cfw_bootloader_pin_groups_41fadc(
    open_cfw_low_init_u32, open_cfw_low_init_u32);
void open_cfw_bootloader_nvic_set_priority_41fdde(
    open_cfw_low_init_u32, open_cfw_low_init_u32);
void open_cfw_bootloader_nvic_enable_irq_41fdc0(open_cfw_low_init_u32);

#if defined(OPEN_CFW_MSPI_LOW_LEVEL_INIT_HOST)
open_cfw_low_init_state *open_cfw_low_init_host_state(void);
void **open_cfw_low_init_host_handle_word(void);
const open_cfw_low_init_u8 *open_cfw_low_init_host_default_config(void);
open_cfw_low_init_u32 open_cfw_low_init_host_call(
    open_cfw_low_init_u32, open_cfw_low_init_word, open_cfw_low_init_word,
    open_cfw_low_init_word);
void open_cfw_low_init_host_log(open_cfw_low_init_u32, open_cfw_low_init_u32,
    open_cfw_low_init_u32);
#endif

static __attribute__((always_inline)) inline open_cfw_low_init_state *
open_cfw_low_init_state_object(void)
{
#if defined(OPEN_CFW_MSPI_LOW_LEVEL_INIT_HOST)
    return open_cfw_low_init_host_state();
#else
    return (open_cfw_low_init_state *)(open_cfw_low_init_word)
        OPEN_CFW_LOW_INIT_STATE_ADDRESS;
#endif
}

static __attribute__((always_inline)) inline void **
open_cfw_low_init_handle_word(void)
{
#if defined(OPEN_CFW_MSPI_LOW_LEVEL_INIT_HOST)
    return open_cfw_low_init_host_handle_word();
#else
    return (void **)(open_cfw_low_init_word)OPEN_CFW_LOW_INIT_HANDLE_ADDRESS;
#endif
}

static __attribute__((always_inline)) inline const open_cfw_low_init_u8 *
open_cfw_low_init_default_config(void)
{
#if defined(OPEN_CFW_MSPI_LOW_LEVEL_INIT_HOST)
    return open_cfw_low_init_host_default_config();
#else
    return (const open_cfw_low_init_u8 *)(open_cfw_low_init_word)
        OPEN_CFW_LOW_INIT_DEFAULT_CONFIG_ADDRESS;
#endif
}

static __attribute__((always_inline)) inline open_cfw_low_init_u32
open_cfw_low_init_call(open_cfw_low_init_u32 operation,
    open_cfw_low_init_word first, open_cfw_low_init_word second,
    open_cfw_low_init_word third)
{
#if defined(OPEN_CFW_MSPI_LOW_LEVEL_INIT_HOST)
    return open_cfw_low_init_host_call(operation, first, second, third);
#else
    (void)third;
    switch (operation) {
    case 0U:
        return ((open_cfw_low_init_initialize_fn)(open_cfw_low_init_word)
            0x00424A5BU)((open_cfw_low_init_u32)first, (void **)second);
    case 1U:
        return ((open_cfw_low_init_power_fn)(open_cfw_low_init_word)
            0x00426809U)((void *)first, (open_cfw_low_init_u32)second,
                (open_cfw_low_init_u32)third);
    case 2U:
        return ((open_cfw_low_init_configure_fn)(open_cfw_low_init_word)
            0x00424AF1U)((void *)first, (const void *)second);
    case 3U:
        return ((open_cfw_low_init_configure_fn)(open_cfw_low_init_word)
            0x00424BE5U)((void *)first, (const void *)second);
    case 4U:
        return ((open_cfw_low_init_handle_fn)(open_cfw_low_init_word)
            0x00425067U)((void *)first);
    case 5U:
        return ((open_cfw_low_init_handle_fn)(open_cfw_low_init_word)
            0x0042516DU)((void *)first);
    case 6U:
        return ((open_cfw_low_init_pin_get_fn)(open_cfw_low_init_word)
            0x0041D90FU)((open_cfw_low_init_u32)first,
                (open_cfw_low_init_u32 *)second);
    case 7U:
        return ((open_cfw_low_init_interrupt_fn)(open_cfw_low_init_word)
            0x00426507U)((void *)first, (open_cfw_low_init_u32)second);
    case 8U:
        return ((open_cfw_low_init_interrupt_fn)(open_cfw_low_init_word)
            0x00426451U)((void *)first, (open_cfw_low_init_u32)second);
    default:
        return ((open_cfw_low_init_master_enable_fn)(open_cfw_low_init_word)
            0x0041B8E1U)();
    }
#endif
}

static __attribute__((always_inline)) inline void open_cfw_low_init_log(
    open_cfw_low_init_u32 level, open_cfw_low_init_u32 line,
    open_cfw_low_init_u32 format)
{
#if defined(OPEN_CFW_MSPI_LOW_LEVEL_INIT_HOST)
    open_cfw_low_init_host_log(level, line, format);
#else
    ((open_cfw_low_init_log_fn)(open_cfw_low_init_word)
        OPEN_CFW_LOW_INIT_LOG_THUMB)(level,
            (const void *)(open_cfw_low_init_word)OPEN_CFW_LOW_INIT_LOG_TAG,
            (const void *)(open_cfw_low_init_word)OPEN_CFW_LOW_INIT_LOG_FILE,
            (const void *)(open_cfw_low_init_word)OPEN_CFW_LOW_INIT_LOG_FUNCTION,
            line, (const void *)(open_cfw_low_init_word)format);
#endif
}

__attribute__((used, noinline))
open_cfw_low_init_u32 open_cfw_bootloader_mspi_low_level_init_420254(
    open_cfw_low_init_u32 instance, const open_cfw_low_init_u8 *device_config,
    open_cfw_low_init_state **output)
{
    open_cfw_low_init_controller_config controller;
    open_cfw_low_init_state *const state = open_cfw_low_init_state_object();
    void **const handle_word = open_cfw_low_init_handle_word();
    const open_cfw_low_init_u8 *selected = device_config;
    open_cfw_low_init_u32 pin_word = 0U;
    open_cfw_low_init_u32 status;

    controller.tcb_words = OPEN_CFW_LOW_INIT_TCB_WORDS;
    controller.tcb_address = OPEN_CFW_LOW_INIT_TCB_ADDRESS;
    controller.clock_on_deepsleep = 0U;

    if (state->initialized != 0U) {
        return (open_cfw_low_init_u32)-1;
    }
    status = open_cfw_low_init_call(0U, instance,
        (open_cfw_low_init_word)handle_word, 0U);
    if (status != 0U) {
        return status;
    }
    status = open_cfw_low_init_call(1U,
        (open_cfw_low_init_word)*handle_word, 0U, 0U);
    if (status != 0U) {
        open_cfw_low_init_log(1U, 0x22AU, OPEN_CFW_LOW_INIT_POWER_FORMAT);
        return 1U;
    }
    status = open_cfw_low_init_call(2U,
        (open_cfw_low_init_word)*handle_word,
        (open_cfw_low_init_word)&controller, 0U);
    if (status != 0U) {
        open_cfw_low_init_log(1U, 0x233U, OPEN_CFW_LOW_INIT_CONFIGURE_FORMAT);
        (void)open_cfw_low_init_call(5U,
            (open_cfw_low_init_word)*handle_word, 0U, 0U);
        return status;
    }
    if (selected == (const open_cfw_low_init_u8 *)0) {
        selected = open_cfw_low_init_default_config();
    }
    status = open_cfw_low_init_call(3U,
        (open_cfw_low_init_word)*handle_word,
        (open_cfw_low_init_word)selected, 0U);
    if (status != 0U) {
        open_cfw_low_init_log(1U, 0x23FU, OPEN_CFW_LOW_INIT_DEVICE_FORMAT);
        (void)open_cfw_low_init_call(5U,
            (open_cfw_low_init_word)*handle_word, 0U, 0U);
        return status;
    }
    status = open_cfw_low_init_call(4U,
        (open_cfw_low_init_word)*handle_word, 0U, 0U);
    if (status != 0U) {
        open_cfw_low_init_log(1U, 0x246U, OPEN_CFW_LOW_INIT_ENABLE_FORMAT);
        (void)open_cfw_low_init_call(5U,
            (open_cfw_low_init_word)*handle_word, 0U, 0U);
        return status;
    }

    open_cfw_bootloader_mspi_xip_config_41ff34(0U);
    open_cfw_bootloader_pin_groups_41fadc(
        instance, OPEN_CFW_LOW_INIT_DEVICE_QUAD_CE0);
    (void)open_cfw_low_init_call(6U, OPEN_CFW_LOW_INIT_CLOCK_PIN,
        (open_cfw_low_init_word)&pin_word, 0U);
    status = open_cfw_low_init_call(7U,
        (open_cfw_low_init_word)*handle_word,
        OPEN_CFW_LOW_INIT_INTERRUPT_MASK, 0U);
    if (status != 0U) {
        return 1U;
    }
    status = open_cfw_low_init_call(8U,
        (open_cfw_low_init_word)*handle_word,
        OPEN_CFW_LOW_INIT_INTERRUPT_MASK, 0U);
    if (status != 0U) {
        open_cfw_low_init_log(1U, 0x269U, OPEN_CFW_LOW_INIT_INTERRUPT_FORMAT);
        return 1U;
    }
    open_cfw_bootloader_nvic_set_priority_41fdde(
        OPEN_CFW_LOW_INIT_MSPI1_IRQ, OPEN_CFW_LOW_INIT_IRQ_PRIORITY);
    open_cfw_bootloader_nvic_enable_irq_41fdc0(OPEN_CFW_LOW_INIT_MSPI1_IRQ);
    (void)open_cfw_low_init_call(9U, 0U, 0U, 0U);

    state->instance = instance;
    state->device_config = selected[OPEN_CFW_LOW_INIT_DEVICE_CONFIG_OFFSET];
    state->handle_word = (open_cfw_low_init_u32)(open_cfw_low_init_word)
        *handle_word;
    state->initialized = 1U;
    *output = state;
    open_cfw_low_init_log(3U, 0x27AU, OPEN_CFW_LOW_INIT_SUCCESS_FORMAT);
    return 0U;
}
