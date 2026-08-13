#include "openr1_cmbacktrace_port.h"

#include <stdarg.h>
#include <stdio.h>
#include <string.h>

#include "FreeRTOS.h"
#include "task.h"

#include "cm_backtrace.h"
#include "openr1_scheduler.h"

#define OPENR1_CRASH_LOG_MAGIC UINT32_C(0x43314252)
#define OPENR1_CRASH_LOG_CAPACITY 2048u
#define OPENR1_CRASH_LINE_CAPACITY 192u
#define OPENR1_TASK_SNAPSHOT_CAPACITY 16u

typedef struct {
    uint32_t magic;
    uint32_t written;
    uint8_t data[OPENR1_CRASH_LOG_CAPACITY];
} openr1_crash_log;

/* NOLOAD keeps the last diagnostic across a watchdog or software reset. */
static openr1_crash_log retained_log
    __attribute__((section(".openr1_noinit"), aligned(4)));

static void ensure_log_initialized(void) {
    if (retained_log.magic != OPENR1_CRASH_LOG_MAGIC ||
        retained_log.written > OPENR1_CRASH_LOG_CAPACITY) {
        memset(&retained_log, 0, sizeof retained_log);
        retained_log.magic = OPENR1_CRASH_LOG_MAGIC;
    }
}

static void append_bytes(const uint8_t *bytes, size_t count) {
    ensure_log_initialized();
    for (size_t index = 0; index < count; ++index) {
        if (retained_log.written == OPENR1_CRASH_LOG_CAPACITY) {
            memmove(retained_log.data, retained_log.data + 1,
                    OPENR1_CRASH_LOG_CAPACITY - 1u);
            retained_log.written--;
        }
        retained_log.data[retained_log.written++] = bytes[index];
    }
}

void openr1_cmbacktrace_log(const char *format, ...) {
    char line[OPENR1_CRASH_LINE_CAPACITY];
    va_list arguments;
    va_start(arguments, format);
    const int rendered = vsnprintf(line, sizeof line, format, arguments);
    va_end(arguments);
    if (rendered > 0) {
        const size_t count = (size_t)rendered < sizeof line
            ? (size_t)rendered : sizeof line - 1u;
        append_bytes((const uint8_t *)line, count);
    }
    static const uint8_t newline[] = {'\r', '\n'};
    append_bytes(newline, sizeof newline);
}

size_t openr1_cmbacktrace_retained_log(uint8_t *output, size_t capacity) {
    ensure_log_initialized();
    if (output == NULL) {
        return retained_log.written;
    }
    const size_t count = retained_log.written < capacity
        ? retained_log.written : capacity;
    memcpy(output, retained_log.data + retained_log.written - count, count);
    return count;
}

void openr1_cmbacktrace_clear_retained_log(void) {
    memset(&retained_log, 0, sizeof retained_log);
    retained_log.magic = OPENR1_CRASH_LOG_MAGIC;
}

void openr1_cmbacktrace_initialize(void) {
    ensure_log_initialized();
    cm_backtrace_init("openR1", "603MV1.9.3", "2.2.6.0009");
}

static const char *task_state_name(eTaskState state) {
    switch (state) {
        case eRunning:
            return "RUNNING";
        case eReady:
            return "READY";
        case eBlocked:
            return "BLOCKED";
        case eSuspended:
            return "SUSPENDED";
        case eDeleted:
            return "DELETED";
        default:
            return "UNKNOWN";
    }
}

void openr1_cmbacktrace_log_task_snapshot(void) {
    TaskStatus_t tasks[OPENR1_TASK_SNAPSHOT_CAPACITY];
    const UBaseType_t count = uxTaskGetSystemState(
        tasks, OPENR1_TASK_SNAPSHOT_CAPACITY, NULL);
    openr1_cmbacktrace_log(
        "Thread ID  Name                 State        Pri StackAddr  StackBytes MinFreeBytes");
    for (UBaseType_t index = 0u; index < count; ++index) {
        const TaskStatus_t *task = &tasks[index];
        uint32_t *stack = (uint32_t *)task->pxStackBase;
        uint32_t stack_words = 0u;
        (void)openr1_scheduler_task_stack(
            (void *)task->xHandle, &stack, &stack_words);
        openr1_cmbacktrace_log(
            "Thread: %4lu %-20s %-12s %3lu 0x%08lx %10lu %12lu",
            (unsigned long)task->xTaskNumber,
            task->pcTaskName != NULL ? task->pcTaskName : "<unnamed>",
            task_state_name(task->eCurrentState),
            (unsigned long)task->uxCurrentPriority,
            (unsigned long)(uintptr_t)stack,
            (unsigned long)(stack_words * sizeof(StackType_t)),
            (unsigned long)(task->usStackHighWaterMark * sizeof(StackType_t)));
    }
    openr1_cmbacktrace_log("Task snapshot complete");
}

/* CmBacktrace's FreeRTOS port contract. These are product adapters, not
 * replacements for the upstream unwinder or private FreeRTOS TCB access. */
uint32_t *vTaskStackAddr(void) {
    uint32_t *start = NULL;
    uint32_t words = 0u;
    (void)openr1_scheduler_current_stack(&start, &words);
    return start;
}

uint32_t vTaskStackSize(void) {
    uint32_t *start = NULL;
    uint32_t words = 0u;
    (void)openr1_scheduler_current_stack(&start, &words);
    return words;
}

char *vTaskName(void) {
    return pcTaskGetName(NULL);
}
