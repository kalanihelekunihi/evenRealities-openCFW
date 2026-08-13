#ifndef OPEN_CFW_FREERTOS_CLI_ORACLE_FREERTOS_H
#define OPEN_CFW_FREERTOS_CLI_ORACLE_FREERTOS_H

#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>

typedef int32_t BaseType_t;
typedef uint32_t UBaseType_t;

#define pdFALSE 0
#define pdTRUE 1
#define pdFAIL 0
#define pdPASS 1
#define configAPPLICATION_PROVIDES_cOutputBuffer 0
#define configCOMMAND_INT_MAX_OUTPUT_SIZE 128
#define configASSERT(expression) do { if (!(expression)) abort(); } while (0)

static inline void *pvPortMalloc(size_t size)
{
    return malloc(size);
}

#endif
