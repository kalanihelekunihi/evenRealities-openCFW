/*
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 * Clean-room reconstruction of the authenticated G2 bootloader delay and
 * initializer-table service cluster.  Fixed ROM/SRAM seams are isolated so
 * the same control flow can be exercised by the host oracle.
 */

typedef __UINT32_TYPE__ open_cfw_boot_service_u32;
typedef __INT32_TYPE__ open_cfw_boot_service_s32;
typedef __UINTPTR_TYPE__ open_cfw_boot_service_uintptr;

enum {
    OPEN_CFW_BOOT_SERVICE_MICROSECONDS_PER_MILLISECOND = 1000U,
    OPEN_CFW_BOOT_SERVICE_INITIALIZER_RECORD_SIZE = 8U,
    OPEN_CFW_BOOT_SERVICE_INITIALIZER_LIMIT = 256U,
    OPEN_CFW_BOOT_SERVICE_INITIALIZER_BEGIN = 0x00433440U,
    OPEN_CFW_BOOT_SERVICE_INITIALIZER_END = 0x00433460U,
    OPEN_CFW_BOOT_SERVICE_INITIALIZER_SCRATCH = 0x20022E00U,
    OPEN_CFW_BOOT_SERVICE_DELAY_THUMB = 0x0041D1C1U,
    OPEN_CFW_BOOT_SERVICE_COPY_THUMB = 0x0041568DU,
    OPEN_CFW_BOOT_SERVICE_SORT_THUMB = 0x00423D09U,
    OPEN_CFW_BOOT_SERVICE_COMPARATOR_THUMB = 0x0041F9F1U
};

typedef struct {
    open_cfw_boot_service_u32 callback;
    open_cfw_boot_service_u32 priority;
} open_cfw_boot_service_initializer;

typedef void (*open_cfw_boot_service_delay_fn)(open_cfw_boot_service_u32);
typedef void *(*open_cfw_boot_service_copy_fn)(
    void *, const void *, open_cfw_boot_service_u32);
typedef open_cfw_boot_service_s32 (*open_cfw_boot_service_compare_fn)(
    const void *, const void *);
typedef void (*open_cfw_boot_service_sort_fn)(
    void *,
    open_cfw_boot_service_u32,
    open_cfw_boot_service_u32,
    open_cfw_boot_service_compare_fn);
typedef void (*open_cfw_boot_service_initializer_fn)(void);

open_cfw_boot_service_s32
open_cfw_bootloader_initializer_priority_compare_41f9f0(
    const void *left,
    const void *right);

#if defined(OPEN_CFW_BOOT_SERVICES_HOST)
void open_cfw_boot_services_host_delay(open_cfw_boot_service_u32 duration);
const open_cfw_boot_service_initializer *
open_cfw_boot_services_host_initializer_begin(void);
open_cfw_boot_service_u32 open_cfw_boot_services_host_initializer_count(void);
open_cfw_boot_service_initializer *
open_cfw_boot_services_host_initializer_scratch(void);
void *open_cfw_boot_services_host_copy(
    void *destination,
    const void *source,
    open_cfw_boot_service_u32 size);
void open_cfw_boot_services_host_sort(
    void *base,
    open_cfw_boot_service_u32 count,
    open_cfw_boot_service_u32 size,
    open_cfw_boot_service_compare_fn compare);
void open_cfw_boot_services_host_invoke(open_cfw_boot_service_u32 callback);
#endif

static __attribute__((always_inline)) inline void
open_cfw_boot_service_delay(open_cfw_boot_service_u32 duration)
{
#if defined(OPEN_CFW_BOOT_SERVICES_HOST)
    open_cfw_boot_services_host_delay(duration);
#else
    ((open_cfw_boot_service_delay_fn)(open_cfw_boot_service_uintptr)
        OPEN_CFW_BOOT_SERVICE_DELAY_THUMB)(duration);
#endif
}

static __attribute__((always_inline)) inline void *
open_cfw_boot_service_copy(
    void *destination,
    const void *source,
    open_cfw_boot_service_u32 size)
{
#if defined(OPEN_CFW_BOOT_SERVICES_HOST)
    return open_cfw_boot_services_host_copy(destination, source, size);
#else
    return ((open_cfw_boot_service_copy_fn)(open_cfw_boot_service_uintptr)
        OPEN_CFW_BOOT_SERVICE_COPY_THUMB)(destination, source, size);
#endif
}

static __attribute__((always_inline)) inline void
open_cfw_boot_service_sort(
    void *base,
    open_cfw_boot_service_u32 count,
    open_cfw_boot_service_u32 size,
    open_cfw_boot_service_compare_fn compare)
{
#if defined(OPEN_CFW_BOOT_SERVICES_HOST)
    open_cfw_boot_services_host_sort(base, count, size, compare);
#else
    ((open_cfw_boot_service_sort_fn)(open_cfw_boot_service_uintptr)
        OPEN_CFW_BOOT_SERVICE_SORT_THUMB)(base, count, size, compare);
#endif
}

static __attribute__((always_inline)) inline void
open_cfw_boot_service_invoke(open_cfw_boot_service_u32 callback)
{
#if defined(OPEN_CFW_BOOT_SERVICES_HOST)
    open_cfw_boot_services_host_invoke(callback);
#else
    ((open_cfw_boot_service_initializer_fn)(open_cfw_boot_service_uintptr)
        callback)();
#endif
}

static __attribute__((always_inline)) inline
open_cfw_boot_service_compare_fn open_cfw_boot_service_comparator(void)
{
#if defined(OPEN_CFW_BOOT_SERVICES_HOST)
    return open_cfw_bootloader_initializer_priority_compare_41f9f0;
#else
    return (open_cfw_boot_service_compare_fn)
        (open_cfw_boot_service_uintptr)
            OPEN_CFW_BOOT_SERVICE_COMPARATOR_THUMB;
#endif
}

__attribute__((used, noinline))
void open_cfw_bootloader_delay_milliseconds_41f9d8(
    open_cfw_boot_service_u32 duration)
{
    open_cfw_boot_service_delay(
        duration * OPEN_CFW_BOOT_SERVICE_MICROSECONDS_PER_MILLISECOND);
}

__attribute__((used, noinline))
void open_cfw_bootloader_delay_41f9e6(open_cfw_boot_service_u32 duration)
{
    open_cfw_boot_service_delay(duration);
}

__attribute__((used, noinline))
open_cfw_boot_service_s32
open_cfw_bootloader_initializer_priority_compare_41f9f0(
    const void *left,
    const void *right)
{
    const open_cfw_boot_service_initializer *const left_initializer =
        (const open_cfw_boot_service_initializer *)left;
    const open_cfw_boot_service_initializer *const right_initializer =
        (const open_cfw_boot_service_initializer *)right;

    return (open_cfw_boot_service_s32)(
        left_initializer->priority - right_initializer->priority);
}

__attribute__((used, noinline))
void open_cfw_bootloader_run_initializers_41f9f8(void)
{
    const open_cfw_boot_service_initializer *begin;
    open_cfw_boot_service_initializer *scratch;
    open_cfw_boot_service_u32 count;
    open_cfw_boot_service_u32 index;

#if defined(OPEN_CFW_BOOT_SERVICES_HOST)
    begin = open_cfw_boot_services_host_initializer_begin();
    count = open_cfw_boot_services_host_initializer_count();
    scratch = open_cfw_boot_services_host_initializer_scratch();
#else
    begin = (const open_cfw_boot_service_initializer *)
        (open_cfw_boot_service_uintptr)
            OPEN_CFW_BOOT_SERVICE_INITIALIZER_BEGIN;
    count = (OPEN_CFW_BOOT_SERVICE_INITIALIZER_END -
             OPEN_CFW_BOOT_SERVICE_INITIALIZER_BEGIN) /
        OPEN_CFW_BOOT_SERVICE_INITIALIZER_RECORD_SIZE;
    scratch = (open_cfw_boot_service_initializer *)
        (open_cfw_boot_service_uintptr)
            OPEN_CFW_BOOT_SERVICE_INITIALIZER_SCRATCH;
#endif

    if (count > OPEN_CFW_BOOT_SERVICE_INITIALIZER_LIMIT) {
        count = OPEN_CFW_BOOT_SERVICE_INITIALIZER_LIMIT;
    }

    (void)open_cfw_boot_service_copy(
        scratch,
        begin,
        count * OPEN_CFW_BOOT_SERVICE_INITIALIZER_RECORD_SIZE);
    open_cfw_boot_service_sort(
        scratch,
        count,
        OPEN_CFW_BOOT_SERVICE_INITIALIZER_RECORD_SIZE,
        open_cfw_boot_service_comparator());

    for (index = 0U; index < count; ++index) {
        if (scratch[index].callback != 0U) {
            open_cfw_boot_service_invoke(scratch[index].callback);
        }
    }
}
