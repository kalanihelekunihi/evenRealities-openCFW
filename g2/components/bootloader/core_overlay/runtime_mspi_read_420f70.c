/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 MX25U25643G guarded read service. */

typedef __UINT8_TYPE__ open_cfw_mspi_read_u8;
typedef __UINT16_TYPE__ open_cfw_mspi_read_u16;
typedef __UINT32_TYPE__ open_cfw_mspi_read_u32;
typedef __UINTPTR_TYPE__ open_cfw_mspi_read_word;

enum {
    OPEN_CFW_MSPI_READ_HANDLE_ADDRESS = 0x200270DCU,
    OPEN_CFW_MSPI_READ_HAL_THUMB = 0x004262E1U,
    OPEN_CFW_MSPI_READ_TIMEOUT = 1000000U,
    OPEN_CFW_MSPI_READ_LIMIT = 0x02000000U,
    OPEN_CFW_MSPI_READ_COMMAND = 0x006CU,
    OPEN_CFW_MSPI_READ_BAD_ARGUMENT = 6U,
    OPEN_CFW_MSPI_READ_BAD_ADDRESS = 5U
};

typedef struct {
    open_cfw_mspi_read_u32 length;
    open_cfw_mspi_read_u8 reserved_04;
    open_cfw_mspi_read_u8 reserved_05;
    open_cfw_mspi_read_u8 reserved_06;
    open_cfw_mspi_read_u8 address_present;
    open_cfw_mspi_read_u32 address;
    open_cfw_mspi_read_u8 instruction_present;
    open_cfw_mspi_read_u8 reserved_13;
    open_cfw_mspi_read_u16 instruction;
    open_cfw_mspi_read_u8 direction;
    open_cfw_mspi_read_u8 reserved_17;
    open_cfw_mspi_read_u8 reserved_18;
    open_cfw_mspi_read_u8 reserved_19;
    open_cfw_mspi_read_u32 buffer;
} open_cfw_mspi_read_descriptor;

_Static_assert(sizeof(open_cfw_mspi_read_descriptor) == 24U,
    "G2 MSPI read descriptor ABI changed");

typedef open_cfw_mspi_read_u32 (*open_cfw_mspi_read_hal_fn)(
    void *, const open_cfw_mspi_read_descriptor *, open_cfw_mspi_read_u32);

#if defined(OPEN_CFW_MSPI_READ_HOST)
open_cfw_mspi_read_word open_cfw_mspi_read_host_handle(void);
void open_cfw_mspi_read_host_event(open_cfw_mspi_read_u32);
open_cfw_mspi_read_u32 open_cfw_mspi_read_host_wait(void);
open_cfw_mspi_read_u32 open_cfw_mspi_read_host_hal(void *,
    const open_cfw_mspi_read_descriptor *, open_cfw_mspi_read_u32);
#else
void open_cfw_bootloader_mspi_guard_enter_41ff08(void);
void open_cfw_bootloader_mspi_set_quad_mode_420e8c(void);
open_cfw_mspi_read_u32
open_cfw_bootloader_mspi_wait_ready_default_4207f4(void);
void open_cfw_bootloader_mspi_guard_exit_41ff1e(void);
#endif

static __attribute__((always_inline)) inline open_cfw_mspi_read_word
open_cfw_mspi_read_handle(void)
{
#if defined(OPEN_CFW_MSPI_READ_HOST)
    return open_cfw_mspi_read_host_handle();
#else
    return *(const volatile open_cfw_mspi_read_u32 *)(open_cfw_mspi_read_word)
        OPEN_CFW_MSPI_READ_HANDLE_ADDRESS;
#endif
}

static __attribute__((always_inline)) inline void
open_cfw_mspi_read_guard_enter(void)
{
#if defined(OPEN_CFW_MSPI_READ_HOST)
    open_cfw_mspi_read_host_event(1U);
#else
    open_cfw_bootloader_mspi_guard_enter_41ff08();
#endif
}

static __attribute__((always_inline)) inline void
open_cfw_mspi_read_quad_mode(void)
{
#if defined(OPEN_CFW_MSPI_READ_HOST)
    open_cfw_mspi_read_host_event(2U);
#else
    open_cfw_bootloader_mspi_set_quad_mode_420e8c();
#endif
}

static __attribute__((always_inline)) inline void open_cfw_mspi_read_wait(void)
{
#if defined(OPEN_CFW_MSPI_READ_HOST)
    open_cfw_mspi_read_host_event(3U);
    (void)open_cfw_mspi_read_host_wait();
#else
    (void)open_cfw_bootloader_mspi_wait_ready_default_4207f4();
#endif
}

static __attribute__((always_inline)) inline open_cfw_mspi_read_u32
open_cfw_mspi_read_hal(void *handle,
    const open_cfw_mspi_read_descriptor *descriptor)
{
#if defined(OPEN_CFW_MSPI_READ_HOST)
    open_cfw_mspi_read_host_event(4U);
    return open_cfw_mspi_read_host_hal(handle, descriptor,
        OPEN_CFW_MSPI_READ_TIMEOUT);
#else
    return ((open_cfw_mspi_read_hal_fn)(open_cfw_mspi_read_word)
        OPEN_CFW_MSPI_READ_HAL_THUMB)(handle, descriptor,
            OPEN_CFW_MSPI_READ_TIMEOUT);
#endif
}

static __attribute__((always_inline)) inline void
open_cfw_mspi_read_guard_exit(void)
{
#if defined(OPEN_CFW_MSPI_READ_HOST)
    open_cfw_mspi_read_host_event(5U);
#else
    open_cfw_bootloader_mspi_guard_exit_41ff1e();
#endif
}

__attribute__((used, noinline))
open_cfw_mspi_read_u32 open_cfw_bootloader_mspi_read_420f70(
    open_cfw_mspi_read_u32 address, void *buffer,
    open_cfw_mspi_read_u32 length)
{
    open_cfw_mspi_read_descriptor descriptor;
    open_cfw_mspi_read_word handle = open_cfw_mspi_read_handle();
    open_cfw_mspi_read_u32 status;

    if (handle == 0U || buffer == (void *)0 || length == 0U) {
        return OPEN_CFW_MSPI_READ_BAD_ARGUMENT;
    }
    if (address >= OPEN_CFW_MSPI_READ_LIMIT) {
        return OPEN_CFW_MSPI_READ_BAD_ADDRESS;
    }

    open_cfw_mspi_read_guard_enter();
    open_cfw_mspi_read_quad_mode();
    open_cfw_mspi_read_wait();

    descriptor.length = length;
    descriptor.reserved_04 = 0U;
    descriptor.reserved_05 = 0U;
    descriptor.reserved_06 = 0U;
    descriptor.address_present = 1U;
    descriptor.address = address;
    descriptor.instruction_present = 1U;
    descriptor.reserved_13 = 0U;
    descriptor.instruction = OPEN_CFW_MSPI_READ_COMMAND;
    descriptor.direction = 1U;
    descriptor.reserved_17 = 0U;
    descriptor.reserved_18 = 0U;
    descriptor.reserved_19 = 0U;
    descriptor.buffer = (open_cfw_mspi_read_u32)
        (open_cfw_mspi_read_word)buffer;

    status = open_cfw_mspi_read_hal((void *)handle, &descriptor);
    open_cfw_mspi_read_guard_exit();
    return status;
}
