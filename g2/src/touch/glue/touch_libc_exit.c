/* SPDX-License-Identifier: MIT
 * G2 touch lite-exit sequence: optional cleanup, stdio hook, terminal halt.
 */
#include <stddef.h>

extern void __call_exitprocs(int, void *) __attribute__((weak));
extern void (*__stdio_exit_handler)(void);
extern void _exit_halt(int) __attribute__((noreturn));

void exit_wrapper(int code) __attribute__((noreturn));

void exit_wrapper(int code)
{
    if (__call_exitprocs)
        __call_exitprocs(code, NULL);

    if (__stdio_exit_handler != NULL)
        (*__stdio_exit_handler)();

    _exit_halt(code);
}
