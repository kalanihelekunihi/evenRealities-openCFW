#ifndef OPENR1_CMBACKTRACE_PORT_H
#define OPENR1_CMBACKTRACE_PORT_H

#include <stddef.h>
#include <stdint.h>

void openr1_cmbacktrace_initialize(void);
void openr1_cmbacktrace_log(const char *format, ...);

/* Read-only access for a future authenticated diagnostic transport. */
size_t openr1_cmbacktrace_retained_log(uint8_t *output, size_t capacity);
void openr1_cmbacktrace_clear_retained_log(void);

#endif /* OPENR1_CMBACKTRACE_PORT_H */
