/* eAT port glue for the AT core (app/a-46-at-core/at_core.c), firmware
 * 2.2.6.10. No source-path or log string is retained; the functions sit
 * between the codec host (service_codec_host.c, ends 0x57dc40) and the
 * FreeRTOS stream buffer (0x57deea), apart from the IAR fmod at 0x57dc40.
 * Native 0x57ddfc..0x57deb0 (literals "%s" 0x57de74, "AT" 0x57de78) and
 * strtok_r 0x57deb0..0x57dee7 (empty string 0x57dee8).
 *
 * AT output channel 2 is the BLE NUS link. Commands flagged
 * G2_AT_CMD_ASYNC run on a short-lived FreeRTOS task ("AT", 0x2000 stack
 * words = 32 KiB, priority 2) that owns a 516-byte heap job holding the
 * handler and copies of both arguments. */
#include <stddef.h>
#include <stdint.h>
#include "g2_at_core.h"

#define AT_PORT_BLE_CHANNEL 2u
#define AT_ASYNC_ARG_SIZE 0x100u
#define AT_ASYNC_STACK_WORDS 0x2000u
#define AT_ASYNC_PRIORITY 2u

typedef struct {
    g2_at_handler_t handler;       /* +0x000 */
    char arg1[AT_ASYNC_ARG_SIZE];  /* +0x004 */
    char arg2[AT_ASYNC_ARG_SIZE];  /* +0x104 */
} g2_at_async_job_t;
_Static_assert(sizeof(g2_at_async_job_t) == 0x204u, "stock 516-byte AT job");

extern void *pvPortMalloc(size_t size);                    /* 0x456110 */
extern void vPortFree(void *block);                        /* 0x456210 */
extern void *xTaskGetCurrentTaskHandle(void);              /* 0x45589c */
extern void audio_task_delete(void *task);                 /* 0x454aae vTaskDelete */
extern int32_t freertos_task_create_4548ba(void (*entry)(void *), const char *name,
                                           uint16_t stack_words, void *argument,
                                           uint32_t priority, void **created); /* xTaskCreate */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t size, const char *format, ...); /* 0x44b728 */
extern uint32_t APP_BleNusSendDataMsg(const uint8_t *data, uint16_t length); /* 0x4be856 */
extern uint32_t iar_strspn_541b52(const char *text, const char *accept);
extern uint32_t iar_strcspn_541b30(const char *text, const char *reject);

static const char at_copy_format[] = "%s";    /* ROM 0x57de74 */
static const char at_task_name[] = "AT";      /* ROM 0x57de78 */
static const char at_empty_string[] = "";     /* ROM 0x57dee8 */

void at_port_init_57ddfc(void);
void at_core_run_async_57de0a(g2_at_handler_t handler, const char *arg1, const char *arg2);
char *strtok_r_57deb0(char *text, const char *delimiters, char **save);

/* 0x57dea4 (no inventory row): AT output channel 2 -> BLE NUS. */
static void at_port_ble_output_57dea4(const char *text, int32_t length)
{
    (void)APP_BleNusSendDataMsg((const uint8_t *)text, (uint16_t)length);
}

/* 0x57de7c (no inventory row): async AT task body. A NULL job or handler
 * skips both the call and the free (the job leaks); the task always
 * deletes itself. */
static void at_port_async_task_57de7c(void *argument)
{
    g2_at_async_job_t *job = (g2_at_async_job_t *)argument;

    if (job != NULL && job->handler != NULL) {
        (void)job->handler(job->arg1, job->arg2);
        vPortFree(job);
    }
    audio_task_delete(xTaskGetCurrentTaskHandle());
}

void at_port_init_57ddfc(void)
{
    at_core_register_callback(AT_PORT_BLE_CHANNEL, at_port_ble_output_57dea4);
}

/* Allocation and task-creation failures are silent; a job whose task
 * fails to start is leaked. */
void at_core_run_async_57de0a(g2_at_handler_t handler, const char *arg1, const char *arg2)
{
    g2_at_async_job_t *job = (g2_at_async_job_t *)pvPortMalloc(sizeof(*job));

    if (job == NULL)
        return;
    (void)aeabi_memset_43c0e4(job, sizeof(*job), 0);
    job->handler = handler;
    if (arg1 != NULL)
        (void)g2_audio_dump_snprintf(job->arg1, AT_ASYNC_ARG_SIZE, at_copy_format, arg1);
    if (arg2 != NULL)
        (void)g2_audio_dump_snprintf(job->arg2, AT_ASYNC_ARG_SIZE, at_copy_format, arg2);
    (void)freertos_task_create_4548ba(at_port_async_task_57de7c, at_task_name,
                                      AT_ASYNC_STACK_WORDS, job, AT_ASYNC_PRIORITY, NULL);
}

/* POSIX strtok_r. At end of input *save points at a static empty string. */
char *strtok_r_57deb0(char *text, const char *delimiters, char **save)
{
    char *token;
    char *end;

    if (text == NULL)
        text = *save;
    token = text + iar_strspn_541b52(text, delimiters);
    if (*token == '\0') {
        *save = (char *)(uintptr_t)at_empty_string;
        return NULL;
    }
    end = token + iar_strcspn_541b30(token, delimiters);
    if (*end != '\0')
        *end++ = '\0';
    *save = end;
    return token;
}
