/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room reconstruction of the G2 2.2.6.10 compact-record core at
 * 0x0043C7CC...0x0043D0C8.  Diagnostics are intentionally omitted; the ring
 * discipline, record format, filtering, pressure scheduling, and persistence
 * cadence are preserved.
 */

#include "compress_log_core.h"
#include "compress_log_port.h"

#include <stdarg.h>
#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_COMPRESS_LOG_MUTEX_TIMEOUT 500u
#define OPEN_CFW_COMPRESS_LOG_PERIOD_TICKS 10000u
#define OPEN_CFW_COMPRESS_LOG_BLOCK_BYTES 4096u
#define OPEN_CFW_COMPRESS_LOG_MAX_BLOCKS 9u
#define OPEN_CFW_COMPRESS_LOG_RECORD_BYTES 44u
#define OPEN_CFW_COMPRESS_LOG_HEADER_BYTES 12u
#define OPEN_CFW_COMPRESS_LOG_ARGUMENT_BYTES 32u
#define OPEN_CFW_COMPRESS_LOG_STRING_BYTES 16u

#ifndef OPEN_CFW_COMPRESS_LOG_RING
#define OPEN_CFW_COMPRESS_LOG_RING \
    (*(volatile struct open_cfw_compress_log_ring *)(uintptr_t)0x200004c8u)
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_MUTEX_HANDLE
#define OPEN_CFW_COMPRESS_LOG_MUTEX_HANDLE \
    (*(void * volatile *)(uintptr_t)0x20074388u)
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_MUTEX_STORAGE
#define OPEN_CFW_COMPRESS_LOG_MUTEX_STORAGE ((void *)(uintptr_t)0x20072998u)
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_SEQUENCE
#define OPEN_CFW_COMPRESS_LOG_SEQUENCE \
    (*(volatile uint8_t *)(uintptr_t)0x20074f9fu)
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_LAST_SYNC_TICK
#define OPEN_CFW_COMPRESS_LOG_LAST_SYNC_TICK \
    (*(volatile uint32_t *)(uintptr_t)0x2007438cu)
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_SYNC_BUFFER
#define OPEN_CFW_COMPRESS_LOG_SYNC_BUFFER \
    ((unsigned char *)(uintptr_t)0x200d4bd8u)
#endif

#ifndef OPEN_CFW_COMPRESS_LOG_MUTEX_CREATE_STATIC
void *open_cfw_freertos_queue_create_mutex_static(unsigned int, void *);
#define OPEN_CFW_COMPRESS_LOG_MUTEX_CREATE_STATIC(type, storage) \
    open_cfw_freertos_queue_create_mutex_static((type), (storage))
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_MUTEX_TAKE_RECURSIVE
int open_cfw_freertos_queue_take_mutex_recursive(void *, unsigned int);
#define OPEN_CFW_COMPRESS_LOG_MUTEX_TAKE_RECURSIVE(handle, timeout) \
    open_cfw_freertos_queue_take_mutex_recursive((handle), (timeout))
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_MUTEX_GIVE_RECURSIVE
int open_cfw_freertos_queue_give_mutex_recursive(void *);
#define OPEN_CFW_COMPRESS_LOG_MUTEX_GIVE_RECURSIVE(handle) \
    open_cfw_freertos_queue_give_mutex_recursive(handle)
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_ENTER_CRITICAL
void open_cfw_freertos_port_enter_critical(void);
#define OPEN_CFW_COMPRESS_LOG_ENTER_CRITICAL() \
    open_cfw_freertos_port_enter_critical()
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_EXIT_CRITICAL
void open_cfw_freertos_port_exit_critical(void);
#define OPEN_CFW_COMPRESS_LOG_EXIT_CRITICAL() \
    open_cfw_freertos_port_exit_critical()
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_SET_INTERRUPT_MASK
unsigned int open_cfw_retained_compress_log_set_interrupt_mask(void);
#define OPEN_CFW_COMPRESS_LOG_SET_INTERRUPT_MASK() \
    open_cfw_retained_compress_log_set_interrupt_mask()
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_CLEAR_INTERRUPT_MASK
void open_cfw_retained_compress_log_clear_interrupt_mask(unsigned int);
#define OPEN_CFW_COMPRESS_LOG_CLEAR_INTERRUPT_MASK(mask) \
    open_cfw_retained_compress_log_clear_interrupt_mask(mask)
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_MODE
uint8_t open_cfw_retained_compress_log_mode(void);
#define OPEN_CFW_COMPRESS_LOG_MODE() open_cfw_retained_compress_log_mode()
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_FILTER_LEVEL
uint8_t open_cfw_retained_compress_log_filter_level(void);
#define OPEN_CFW_COMPRESS_LOG_FILTER_LEVEL() \
    open_cfw_retained_compress_log_filter_level()
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_TICK_COUNT
uint32_t open_cfw_cmsis_kernel_get_tick_count(void);
#define OPEN_CFW_COMPRESS_LOG_TICK_COUNT() \
    open_cfw_cmsis_kernel_get_tick_count()
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_WALL_TIME
uint32_t open_cfw_wall_time_seconds(void);
#define OPEN_CFW_COMPRESS_LOG_WALL_TIME() open_cfw_wall_time_seconds()
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_PRESSURE_ALLOWED_A
int open_cfw_retained_compress_log_pressure_allowed_a(void);
#define OPEN_CFW_COMPRESS_LOG_PRESSURE_ALLOWED_A() \
    open_cfw_retained_compress_log_pressure_allowed_a()
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_PRESSURE_ALLOWED_B
int open_cfw_retained_compress_log_pressure_allowed_b(void);
#define OPEN_CFW_COMPRESS_LOG_PRESSURE_ALLOWED_B() \
    open_cfw_retained_compress_log_pressure_allowed_b()
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_SCHEDULE_SYNC
void open_cfw_retained_compress_log_schedule_sync(void);
#define OPEN_CFW_COMPRESS_LOG_SCHEDULE_SYNC() \
    open_cfw_retained_compress_log_schedule_sync()
#endif
#ifndef OPEN_CFW_COMPRESS_LOG_EXCEPTION_NUMBER
static __attribute__((unused)) inline uint32_t
open_cfw_compress_log_exception_number_default(void)
{
#if defined(__arm__) || defined(__thumb__)
    uint32_t exception_number;
    __asm volatile("mrs %0, ipsr" : "=r"(exception_number));
    return exception_number & 0x1fu;
#else
    return 0u;
#endif
}
#define OPEN_CFW_COMPRESS_LOG_EXCEPTION_NUMBER() \
    open_cfw_compress_log_exception_number_default()
#endif

#if !defined(OPEN_CFW_COMPRESS_LOG_CORE_MUTEX_INIT_ONLY) && \
    !defined(OPEN_CFW_COMPRESS_LOG_CORE_RING_READ_LOCKED_ONLY) && \
    !defined(OPEN_CFW_COMPRESS_LOG_CORE_GET_ALL_ONLY) && \
    !defined(OPEN_CFW_COMPRESS_LOG_CORE_RING_WRITE_ONLY) && \
    !defined(OPEN_CFW_COMPRESS_LOG_CORE_ENCODE_ONLY) && \
    !defined(OPEN_CFW_COMPRESS_LOG_CORE_OUTPUT_ONLY) && \
    !defined(OPEN_CFW_COMPRESS_LOG_CORE_PERIODIC_SYNC_ONLY) && \
    !defined(OPEN_CFW_COMPRESS_LOG_CORE_FORCE_SYNC_ONLY)
#define OPEN_CFW_COMPRESS_LOG_CORE_BUILD_ALL 1
#endif

static __attribute__((unused)) void open_cfw_compress_log_copy(
    unsigned char *destination,
    const unsigned char *source,
    uint32_t size
)
{
    while (size != 0u) {
        *destination++ = *source++;
        --size;
    }
}

static __attribute__((unused)) void open_cfw_compress_log_zero(
    unsigned char *destination, uint32_t size
)
{
    while (size != 0u) {
        *destination++ = 0u;
        --size;
    }
}

static __attribute__((unused)) uint32_t
open_cfw_compress_log_string_length(const char *text)
{
    uint32_t size = 0u;
    if (text != NULL) {
        while (text[size] != '\0') {
            ++size;
        }
    }
    return size;
}

static __attribute__((unused)) int open_cfw_compress_log_ring_valid(void)
{
    return OPEN_CFW_COMPRESS_LOG_RING.buffer != NULL &&
        OPEN_CFW_COMPRESS_LOG_RING.capacity > 1u &&
        OPEN_CFW_COMPRESS_LOG_RING.read_offset <
            OPEN_CFW_COMPRESS_LOG_RING.capacity &&
        OPEN_CFW_COMPRESS_LOG_RING.write_offset <
            OPEN_CFW_COMPRESS_LOG_RING.capacity;
}

static __attribute__((unused)) uint32_t open_cfw_compress_log_available(void)
{
    uint32_t read_offset = OPEN_CFW_COMPRESS_LOG_RING.read_offset;
    uint32_t write_offset = OPEN_CFW_COMPRESS_LOG_RING.write_offset;
    uint32_t capacity = OPEN_CFW_COMPRESS_LOG_RING.capacity;
    return write_offset >= read_offset
        ? write_offset - read_offset
        : capacity - read_offset + write_offset;
}

static __attribute__((unused)) void open_cfw_compress_log_copy_from_ring(
    unsigned char *destination,
    uint32_t size
)
{
    uint32_t read_offset = OPEN_CFW_COMPRESS_LOG_RING.read_offset;
    uint32_t capacity = OPEN_CFW_COMPRESS_LOG_RING.capacity;
    uint32_t first = capacity - read_offset;
    if (first > size) {
        first = size;
    }
    open_cfw_compress_log_copy(
        destination, OPEN_CFW_COMPRESS_LOG_RING.buffer + read_offset, first
    );
    open_cfw_compress_log_copy(
        destination + first, OPEN_CFW_COMPRESS_LOG_RING.buffer, size - first
    );
    OPEN_CFW_COMPRESS_LOG_RING.read_offset =
        size - first == 0u ? read_offset + first : size - first;
    if (OPEN_CFW_COMPRESS_LOG_RING.read_offset == capacity) {
        OPEN_CFW_COMPRESS_LOG_RING.read_offset = 0u;
    }
}

#if defined(OPEN_CFW_COMPRESS_LOG_CORE_BUILD_ALL) || \
    defined(OPEN_CFW_COMPRESS_LOG_CORE_MUTEX_INIT_ONLY)
__attribute__((used, noinline))
void open_cfw_compress_log_mutex_init(void)
{
    if (OPEN_CFW_COMPRESS_LOG_MUTEX_HANDLE == NULL) {
        OPEN_CFW_COMPRESS_LOG_MUTEX_HANDLE =
            OPEN_CFW_COMPRESS_LOG_MUTEX_CREATE_STATIC(
                4u, OPEN_CFW_COMPRESS_LOG_MUTEX_STORAGE
            );
        if (OPEN_CFW_COMPRESS_LOG_MUTEX_HANDLE == NULL) {
            (void)OPEN_CFW_COMPRESS_LOG_SET_INTERRUPT_MASK();
            for (;;) {
            }
        }
    }
}
#endif

#if defined(OPEN_CFW_COMPRESS_LOG_CORE_BUILD_ALL) || \
    defined(OPEN_CFW_COMPRESS_LOG_CORE_RING_READ_LOCKED_ONLY)
__attribute__((used, noinline))
int open_cfw_compress_log_ring_read_locked(void *destination, uint16_t size)
{
    uint32_t available;
    if (OPEN_CFW_COMPRESS_LOG_EXCEPTION_NUMBER() != 0u ||
        OPEN_CFW_COMPRESS_LOG_MUTEX_HANDLE == NULL ||
        OPEN_CFW_COMPRESS_LOG_MUTEX_TAKE_RECURSIVE(
            OPEN_CFW_COMPRESS_LOG_MUTEX_HANDLE,
            OPEN_CFW_COMPRESS_LOG_MUTEX_TIMEOUT
        ) != 1) {
        return 0;
    }
    if (!open_cfw_compress_log_ring_valid()) {
        (void)OPEN_CFW_COMPRESS_LOG_MUTEX_GIVE_RECURSIVE(
            OPEN_CFW_COMPRESS_LOG_MUTEX_HANDLE
        );
        return 0;
    }
    available = open_cfw_compress_log_available();
    if (available <= (uint32_t)size + 1u) {
        (void)OPEN_CFW_COMPRESS_LOG_MUTEX_GIVE_RECURSIVE(
            OPEN_CFW_COMPRESS_LOG_MUTEX_HANDLE
        );
        return 0;
    }
    open_cfw_compress_log_copy_from_ring(destination, size);
    (void)OPEN_CFW_COMPRESS_LOG_MUTEX_GIVE_RECURSIVE(
        OPEN_CFW_COMPRESS_LOG_MUTEX_HANDLE
    );
    return 1;
}
#endif

#if defined(OPEN_CFW_COMPRESS_LOG_CORE_BUILD_ALL) || \
    defined(OPEN_CFW_COMPRESS_LOG_CORE_GET_ALL_ONLY)
__attribute__((used, noinline))
int open_cfw_compress_log_get_all_buffer(void *destination, uint16_t size)
{
    uint32_t interrupt_mask = 0u;
    int exception_mode;
    if (!open_cfw_compress_log_ring_valid() ||
        open_cfw_compress_log_available() < (uint32_t)size) {
        return 0;
    }
    exception_mode = OPEN_CFW_COMPRESS_LOG_EXCEPTION_NUMBER() != 0u;
    if (exception_mode) {
        interrupt_mask = OPEN_CFW_COMPRESS_LOG_SET_INTERRUPT_MASK();
    } else {
        OPEN_CFW_COMPRESS_LOG_ENTER_CRITICAL();
    }
    open_cfw_compress_log_copy_from_ring(destination, size);
    if (exception_mode) {
        OPEN_CFW_COMPRESS_LOG_CLEAR_INTERRUPT_MASK(interrupt_mask);
    } else {
        OPEN_CFW_COMPRESS_LOG_EXIT_CRITICAL();
    }
    return 1;
}
#endif

#if defined(OPEN_CFW_COMPRESS_LOG_CORE_BUILD_ALL) || \
    defined(OPEN_CFW_COMPRESS_LOG_CORE_RING_WRITE_ONLY)
__attribute__((used, noinline))
int open_cfw_compress_log_ring_write(const void *source, uint16_t size)
{
    uint32_t available;
    uint32_t free_bytes;
    uint32_t write_offset;
    uint32_t first;
    uint32_t used_after;
    int schedule = 0;
    uint8_t mode;
    if (OPEN_CFW_COMPRESS_LOG_EXCEPTION_NUMBER() != 0u ||
        OPEN_CFW_COMPRESS_LOG_MUTEX_HANDLE == NULL ||
        OPEN_CFW_COMPRESS_LOG_MUTEX_TAKE_RECURSIVE(
            OPEN_CFW_COMPRESS_LOG_MUTEX_HANDLE,
            OPEN_CFW_COMPRESS_LOG_MUTEX_TIMEOUT
        ) != 1) {
        return 0;
    }
    if (!open_cfw_compress_log_ring_valid()) {
        schedule = 1;
    } else {
        available = open_cfw_compress_log_available();
        free_bytes = OPEN_CFW_COMPRESS_LOG_RING.capacity - available - 1u;
        if ((uint32_t)size >= free_bytes) {
            schedule = 1;
        } else {
            write_offset = OPEN_CFW_COMPRESS_LOG_RING.write_offset;
            first = OPEN_CFW_COMPRESS_LOG_RING.capacity - write_offset;
            if (first > (uint32_t)size) {
                first = size;
            }
            open_cfw_compress_log_copy(
                OPEN_CFW_COMPRESS_LOG_RING.buffer + write_offset,
                source,
                first
            );
            open_cfw_compress_log_copy(
                OPEN_CFW_COMPRESS_LOG_RING.buffer,
                (const unsigned char *)source + first,
                (uint32_t)size - first
            );
            OPEN_CFW_COMPRESS_LOG_RING.write_offset =
                (write_offset + (uint32_t)size) %
                OPEN_CFW_COMPRESS_LOG_RING.capacity;
            used_after = available + (uint32_t)size + 1u;
            mode = OPEN_CFW_COMPRESS_LOG_MODE();
            if ((mode & 4u) != 0u) {
                schedule = used_after >= 236u;
            } else if ((mode & 1u) != 0u) {
                schedule = used_after >= OPEN_CFW_COMPRESS_LOG_BLOCK_BYTES;
            }
        }
    }
    (void)OPEN_CFW_COMPRESS_LOG_MUTEX_GIVE_RECURSIVE(
        OPEN_CFW_COMPRESS_LOG_MUTEX_HANDLE
    );
    if (schedule != 0 && (OPEN_CFW_COMPRESS_LOG_MODE() & 1u) != 0u &&
        (OPEN_CFW_COMPRESS_LOG_PRESSURE_ALLOWED_A() == 0 ||
         OPEN_CFW_COMPRESS_LOG_PRESSURE_ALLOWED_B() == 0)) {
        OPEN_CFW_COMPRESS_LOG_SCHEDULE_SYNC();
    }
    return schedule == 0;
}
#endif

#if defined(OPEN_CFW_COMPRESS_LOG_CORE_BUILD_ALL) || \
    defined(OPEN_CFW_COMPRESS_LOG_CORE_ENCODE_ONLY)
__attribute__((used, noinline))
void open_cfw_compress_log_encode_record(
    uint32_t metadata,
    const char *format,
    va_list *arguments
)
{
    unsigned char record[OPEN_CFW_COMPRESS_LOG_RECORD_BYTES];
    uint32_t argument_bytes = 0u;
    uint32_t argument_count = 0u;
    uint32_t maximum_arguments = (metadata >> 22) & 0x0fu;
    uint32_t level = (metadata >> 26) & 7u;
    uint32_t sequence;
    uint32_t tick;
    uint32_t word;
    uint8_t mode = OPEN_CFW_COMPRESS_LOG_MODE();

    if (((mode & 4u) != 0u && level > 5u) ||
        ((mode & 1u) != 0u && level > OPEN_CFW_COMPRESS_LOG_FILTER_LEVEL())) {
        return;
    }
    open_cfw_compress_log_zero(record, sizeof(record));
    sequence = OPEN_CFW_COMPRESS_LOG_SEQUENCE++;
    tick = OPEN_CFW_COMPRESS_LOG_TICK_COUNT() % 1000u;
    word = 0xDC00007Bu | ((sequence & 0xffu) << 8) |
        ((tick & 0x3ffu) << 16);
    open_cfw_compress_log_copy(record, (const unsigned char *)&word, 4u);
    word = OPEN_CFW_COMPRESS_LOG_WALL_TIME();
    open_cfw_compress_log_copy(record + 4u, (const unsigned char *)&word, 4u);
    open_cfw_compress_log_copy(record + 8u,
        (const unsigned char *)&metadata, 4u);

    while (*format != '\0' && argument_bytes < OPEN_CFW_COMPRESS_LOG_ARGUMENT_BYTES &&
           argument_count < maximum_arguments) {
        int long_long_value = 0;
        char conversion;
        if (*format++ != '%') {
            continue;
        }
        if (*format == '0' || *format == '-' || *format == '+' ||
            *format == ' ' || *format == '#') {
            ++format;
        }
        while (*format >= '0' && *format <= '9') {
            ++format;
        }
        if (*format == '.') {
            ++format;
            if (*format == '*') {
                (void)va_arg(*arguments, int);
                ++format;
            } else {
                while (*format >= '0' && *format <= '9') {
                    ++format;
                }
            }
        }
        if (*format == 'l') {
            ++format;
            if (*format == 'l') {
                long_long_value = 1;
                ++format;
            }
        } else if (*format == 'h') {
            ++format;
            if (*format == 'h') {
                ++format;
            }
        }
        conversion = *format;
        if (conversion == '\0') {
            break;
        }
        if (conversion == '%') {
            ++format;
            continue;
        }
        if (conversion == 's') {
            const char *text = va_arg(*arguments, const char *);
            if (argument_bytes + OPEN_CFW_COMPRESS_LOG_STRING_BYTES <=
                OPEN_CFW_COMPRESS_LOG_ARGUMENT_BYTES) {
                uint32_t length = open_cfw_compress_log_string_length(text);
                uint32_t copied = length > OPEN_CFW_COMPRESS_LOG_STRING_BYTES
                    ? OPEN_CFW_COMPRESS_LOG_STRING_BYTES : length;
                uint32_t skip = length - copied;
                if (copied != 0u) {
                    open_cfw_compress_log_copy(
                        record + OPEN_CFW_COMPRESS_LOG_HEADER_BYTES +
                            argument_bytes,
                        (const unsigned char *)text + skip,
                        copied
                    );
                }
                open_cfw_compress_log_zero(
                    record + OPEN_CFW_COMPRESS_LOG_HEADER_BYTES +
                        argument_bytes + copied,
                    OPEN_CFW_COMPRESS_LOG_STRING_BYTES - copied
                );
                argument_bytes += OPEN_CFW_COMPRESS_LOG_STRING_BYTES;
            }
        } else if (conversion == 'f' || conversion == 'F') {
            double promoted = va_arg(*arguments, double);
            if (argument_bytes + 4u <= OPEN_CFW_COMPRESS_LOG_ARGUMENT_BYTES) {
                float value = (float)promoted;
                open_cfw_compress_log_copy(
                    record + OPEN_CFW_COMPRESS_LOG_HEADER_BYTES + argument_bytes,
                    (const unsigned char *)&value,
                    4u
                );
                argument_bytes += 4u;
            }
        } else {
            uint32_t value = long_long_value != 0
                ? (uint32_t)va_arg(*arguments, unsigned long long)
                : va_arg(*arguments, uint32_t);
            if (argument_bytes + 4u <= OPEN_CFW_COMPRESS_LOG_ARGUMENT_BYTES) {
                open_cfw_compress_log_copy(
                    record + OPEN_CFW_COMPRESS_LOG_HEADER_BYTES + argument_bytes,
                    (const unsigned char *)&value,
                    4u
                );
                argument_bytes += 4u;
            }
        }
        ++argument_count;
        ++format;
    }
    metadata = (metadata & 0xFC3FFFFFu) |
        ((argument_count & 0x0fu) << 22);
    open_cfw_compress_log_copy(record + 8u,
        (const unsigned char *)&metadata, 4u);
    (void)open_cfw_compress_log_ring_write(
        record,
        (uint16_t)(OPEN_CFW_COMPRESS_LOG_HEADER_BYTES + argument_bytes)
    );
}
#endif

#if defined(OPEN_CFW_COMPRESS_LOG_CORE_BUILD_ALL) || \
    defined(OPEN_CFW_COMPRESS_LOG_CORE_OUTPUT_ONLY)
__attribute__((used, noinline))
void open_cfw_compress_log_output(
    uint32_t metadata,
    uintptr_t identity,
    const char *format,
    ...
)
{
    va_list arguments;
    if (open_cfw_compress_log_export_active() != 0u ||
        OPEN_CFW_COMPRESS_LOG_EXCEPTION_NUMBER() != 0u ||
        OPEN_CFW_COMPRESS_LOG_MUTEX_HANDLE == NULL ||
        OPEN_CFW_COMPRESS_LOG_MUTEX_TAKE_RECURSIVE(
            OPEN_CFW_COMPRESS_LOG_MUTEX_HANDLE,
            OPEN_CFW_COMPRESS_LOG_MUTEX_TIMEOUT
        ) != 1) {
        return;
    }
    va_start(arguments, format);
    open_cfw_compress_log_encode_record(
        (metadata & 0xFFC00000u) | ((uint32_t)identity & 0x003FFFFFu),
        format,
        &arguments
    );
    va_end(arguments);
    (void)OPEN_CFW_COMPRESS_LOG_MUTEX_GIVE_RECURSIVE(
        OPEN_CFW_COMPRESS_LOG_MUTEX_HANDLE
    );
}
#endif

#if defined(OPEN_CFW_COMPRESS_LOG_CORE_BUILD_ALL) || \
    defined(OPEN_CFW_COMPRESS_LOG_CORE_PERIODIC_SYNC_ONLY)
__attribute__((used, noinline))
void open_cfw_compress_log_periodic_sync(void)
{
    uint32_t now = OPEN_CFW_COMPRESS_LOG_TICK_COUNT();
    uint32_t blocks = 0u;
    if (OPEN_CFW_COMPRESS_LOG_LAST_SYNC_TICK +
        OPEN_CFW_COMPRESS_LOG_PERIOD_TICKS >= now) {
        return;
    }
    OPEN_CFW_COMPRESS_LOG_LAST_SYNC_TICK = now;
    while (blocks < OPEN_CFW_COMPRESS_LOG_MAX_BLOCKS &&
           open_cfw_compress_log_ring_read_locked(
               OPEN_CFW_COMPRESS_LOG_SYNC_BUFFER,
               OPEN_CFW_COMPRESS_LOG_BLOCK_BYTES
           ) != 0) {
        ++blocks;
        open_cfw_compress_log_sync_to_files(
            OPEN_CFW_COMPRESS_LOG_SYNC_BUFFER,
            OPEN_CFW_COMPRESS_LOG_BLOCK_BYTES
        );
    }
}
#endif

#if defined(OPEN_CFW_COMPRESS_LOG_CORE_BUILD_ALL) || \
    defined(OPEN_CFW_COMPRESS_LOG_CORE_FORCE_SYNC_ONLY)
__attribute__((used, noinline))
void open_cfw_compress_log_force_sync(void)
{
    uint32_t blocks = 0u;
    uint32_t remainder;
    while (blocks < OPEN_CFW_COMPRESS_LOG_MAX_BLOCKS &&
           open_cfw_compress_log_ring_read_locked(
               OPEN_CFW_COMPRESS_LOG_SYNC_BUFFER,
               OPEN_CFW_COMPRESS_LOG_BLOCK_BYTES
           ) != 0) {
        ++blocks;
        open_cfw_compress_log_sync_to_files(
            OPEN_CFW_COMPRESS_LOG_SYNC_BUFFER,
            OPEN_CFW_COMPRESS_LOG_BLOCK_BYTES
        );
    }
    if (!open_cfw_compress_log_ring_valid()) {
        return;
    }
    remainder = open_cfw_compress_log_available();
    if (remainder != 0u && remainder <= 0xffffu &&
        open_cfw_compress_log_get_all_buffer(
            OPEN_CFW_COMPRESS_LOG_SYNC_BUFFER, (uint16_t)remainder
        ) != 0) {
        open_cfw_compress_log_sync_to_files(
            OPEN_CFW_COMPRESS_LOG_SYNC_BUFFER, remainder
        );
    }
}
#endif
