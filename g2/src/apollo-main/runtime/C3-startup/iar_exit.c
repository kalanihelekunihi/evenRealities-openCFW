/* IAR DLIB exit / _exit for the Apollo main image, reconstructed from the
 * 2.2.6.10 disassembly (no source path is retained).
 *
 * Stock ranges:
 *   0x005e42dc..0x005e42df  exit  (b.w _exit; no atexit/stream teardown is
 *                           linked)
 *   0x005e42e0..0x005e42e9  _exit (keeps the status in r7 and calls __exit
 *                           0x585120 forever; 0x5e42ea is padding)
 * exit is reached only from __cmain 0x5e42ae (C3-startup/iar_cmain.c).
 *
 * __exit 0x585120 is g2_main_formatter_exit
 * (system/log/full-formatter/full-formatter-native/termination.c): semihosting
 * SYS_EXIT (0x18, ADP_Stopped 0x20026). Its definition is a naked (void)
 * function that overwrites r0; stock _exit still moves the status into r0
 * before each call, which the IAR __exit(int) prototype here reproduces.
 *
 * Profile g2-apollo-main-2. */
#include <stdint.h>

/* Stock 0x585120 (IAR __exit), termination.c. */
extern void g2_main_formatter_exit(int32_t status);

void iar_exit_loop_5e42e0(int32_t status) __attribute__((noreturn));
void iar_exit_5e42dc(int32_t status) __attribute__((noreturn));

/* Stock 0x005e42e0 (_exit) */
void iar_exit_loop_5e42e0(int32_t status)
{
    for (;;)
        g2_main_formatter_exit(status);
}

/* Stock 0x005e42dc (exit) */
void iar_exit_5e42dc(int32_t status)
{
    iar_exit_loop_5e42e0(status);
}
