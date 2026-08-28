/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the bounded G2 MX25U25643G read transfer. */

typedef __UINT8_TYPE__ open_cfw_read_transfer_u8;
typedef __UINT16_TYPE__ open_cfw_read_transfer_u16;
typedef __UINT32_TYPE__ open_cfw_read_transfer_u32;
typedef __UINTPTR_TYPE__ open_cfw_read_transfer_word;

enum {
    OPEN_CFW_READ_TRANSFER_HANDLE_SLOT = 0x200270DCU,
    OPEN_CFW_READ_TRANSFER_HAL_THUMB = 0x004262E1U,
    OPEN_CFW_READ_TRANSFER_LOG_THUMB = 0x00415FAFU,
    OPEN_CFW_READ_TRANSFER_LOG_FORMAT = 0x00431420U,
    OPEN_CFW_READ_TRANSFER_TIMEOUT = 1000000U,
    OPEN_CFW_READ_TRANSFER_MAX_ADDRESS = 0x02000000U,
    OPEN_CFW_READ_TRANSFER_NO_HANDLE = 2U,
    OPEN_CFW_READ_TRANSFER_BAD_ADDRESS = 5U,
    OPEN_CFW_READ_TRANSFER_BAD_BUFFER = 6U
};

typedef struct {
    open_cfw_read_transfer_u32 length;
    open_cfw_read_transfer_u8 reserved_04;
    open_cfw_read_transfer_u8 reserved_05;
    open_cfw_read_transfer_u8 reserved_06;
    open_cfw_read_transfer_u8 address_present;
    open_cfw_read_transfer_u32 address;
    open_cfw_read_transfer_u8 instruction_present;
    open_cfw_read_transfer_u8 reserved_13;
    open_cfw_read_transfer_u16 instruction;
    open_cfw_read_transfer_u8 direction;
    open_cfw_read_transfer_u8 reserved_17;
    open_cfw_read_transfer_u8 reserved_18;
    open_cfw_read_transfer_u8 reserved_19;
    open_cfw_read_transfer_u32 buffer;
} open_cfw_read_transfer_descriptor;

_Static_assert(sizeof(open_cfw_read_transfer_descriptor) == 24U,
    "G2 MSPI transfer descriptor ABI changed");

typedef open_cfw_read_transfer_u32 (*open_cfw_read_transfer_hal_fn)(
    void *, const open_cfw_read_transfer_descriptor *,
    open_cfw_read_transfer_u32);
typedef open_cfw_read_transfer_u32 (*open_cfw_read_transfer_log_fn)(
    const void *, ...);

#if defined(OPEN_CFW_MSPI_READ_TRANSFER_HOST)
void *open_cfw_read_transfer_host_handle(void);
open_cfw_read_transfer_u32 open_cfw_read_transfer_host_hal(
    void *, const open_cfw_read_transfer_descriptor *,
    open_cfw_read_transfer_u32);
void open_cfw_read_transfer_host_log(
    open_cfw_read_transfer_u32, open_cfw_read_transfer_u32,
    open_cfw_read_transfer_u32, open_cfw_read_transfer_u32);
#endif

static __attribute__((always_inline)) inline void *open_cfw_read_transfer_handle(void)
{
#if defined(OPEN_CFW_MSPI_READ_TRANSFER_HOST)
    return open_cfw_read_transfer_host_handle();
#else
    return *(void **)(open_cfw_read_transfer_word)
        OPEN_CFW_READ_TRANSFER_HANDLE_SLOT;
#endif
}

static __attribute__((always_inline)) inline open_cfw_read_transfer_u32
open_cfw_read_transfer_hal(void *handle,
    const open_cfw_read_transfer_descriptor *descriptor)
{
#if defined(OPEN_CFW_MSPI_READ_TRANSFER_HOST)
    return open_cfw_read_transfer_host_hal(
        handle, descriptor, OPEN_CFW_READ_TRANSFER_TIMEOUT);
#else
    return ((open_cfw_read_transfer_hal_fn)(open_cfw_read_transfer_word)
        OPEN_CFW_READ_TRANSFER_HAL_THUMB)(
            handle, descriptor, OPEN_CFW_READ_TRANSFER_TIMEOUT);
#endif
}

static __attribute__((always_inline)) inline void open_cfw_read_transfer_log(
    open_cfw_read_transfer_u32 instruction,
    open_cfw_read_transfer_u32 address,
    open_cfw_read_transfer_u32 length,
    open_cfw_read_transfer_u32 status)
{
#if defined(OPEN_CFW_MSPI_READ_TRANSFER_HOST)
    open_cfw_read_transfer_host_log(instruction, address, length, status);
#else
    (void)((open_cfw_read_transfer_log_fn)(open_cfw_read_transfer_word)
        OPEN_CFW_READ_TRANSFER_LOG_THUMB)(
            (const void *)(open_cfw_read_transfer_word)
                OPEN_CFW_READ_TRANSFER_LOG_FORMAT,
            instruction, address, length, status);
#endif
}

__attribute__((used, noinline))
open_cfw_read_transfer_u32 open_cfw_bootloader_mspi_read_transfer_4205f4(
    open_cfw_read_transfer_u32 instruction,
    open_cfw_read_transfer_u32 address,
    open_cfw_read_transfer_u32 address_present,
    void *buffer,
    open_cfw_read_transfer_u32 length)
{
    open_cfw_read_transfer_descriptor descriptor;
    void *const handle = open_cfw_read_transfer_handle();
    open_cfw_read_transfer_u32 status;

    if (handle == (void *)0) {
        return OPEN_CFW_READ_TRANSFER_NO_HANDLE;
    }
    if (buffer == (void *)0 || length == 0U) {
        return OPEN_CFW_READ_TRANSFER_BAD_BUFFER;
    }
    if (address >= OPEN_CFW_READ_TRANSFER_MAX_ADDRESS) {
        return OPEN_CFW_READ_TRANSFER_BAD_ADDRESS;
    }

    descriptor.length = length;
    descriptor.reserved_04 = 0U;
    descriptor.reserved_05 = 0U;
    descriptor.reserved_06 = 0U;
    descriptor.address_present = (open_cfw_read_transfer_u8)
        (address_present != 0U);
    descriptor.address = address_present != 0U ? address : 0U;
    descriptor.instruction_present = 1U;
    descriptor.reserved_13 = 0U;
    descriptor.instruction = (open_cfw_read_transfer_u16)instruction;
    descriptor.direction = 1U;
    descriptor.reserved_17 = 0U;
    descriptor.reserved_18 = 0U;
    descriptor.reserved_19 = 0U;
    descriptor.buffer = (open_cfw_read_transfer_u32)
        (open_cfw_read_transfer_word)buffer;

    status = open_cfw_read_transfer_hal(handle, &descriptor);
    if (status != 0U) {
        open_cfw_read_transfer_log(
            (open_cfw_read_transfer_u16)instruction,
            address, length, status);
    }
    return status;
}
