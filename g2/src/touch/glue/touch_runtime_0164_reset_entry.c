/* SPDX-License-Identifier: MIT
 * Stock touch_runtime_0164_reset_entry @ VA 0x3464
 * Evidence: corpus touch/ghidra/open-2026-09-29/functions-000.jsonl +
 * decomp/00003464.c; image base 0x3300 + offset 0x164; body 0x3464..0x34d7,
 * 114 B, sha256 c11a048f4301cb2d….
 *
 * Callees: touch_runtime_0158_stack_limit @ 0x3458,
 * touch_product_09b4_run @ 0x3cb4, touch_terminal_1368_passthrough @ 0x4668,
 * exit_wrapper @ 0xa9ac, memset @ 0xa9d4, __libc_init_array @ 0xa9e4.
 *
 * Not byte-identical: freestanding CRT shape matching that call graph.
 */
#include <stdint.h>
#include <stddef.h>

extern uint32_t __data_load_start;
extern uint32_t __data_start;
extern uint32_t __data_end;
extern uint32_t __bss_start;
extern uint32_t __bss_end;

extern void *memset(void *dst, int c, size_t n);
extern void *memcpy(void *dst, const void *src, size_t n);
extern int touch_product_09b4_run(void);

/* Evidence: stock 0x3458 touch_runtime_0158_stack_limit, 10 B,
 * sha256 c36ba6f99ebece2e…; corpus decomp/00003458.c is empty return;
 * CM0+ has no MSPLIM — pure no-op matches decompile + size. */
void touch_runtime_0158_stack_limit(void)
{
}

/* The locked reset copy contains one init and one fini entry. */
extern void frame_dummy(void);
extern void __do_global_dtors_aux(void);

typedef void (*touch_crt_hook)(void);
const touch_crt_hook touch_crt_arrays[2]
    __attribute__((section(".touch_init.crt_arrays"), used)) = {
        frame_dummy,
        __do_global_dtors_aux,
    };

extern void __libc_init_array(void);

/* The newlib init-array loop calls the empty legacy init hook. */
__attribute__((noinline, used)) void _init(void)
{
}

/* Stock terminal loop @ 0xaa40. The C exit wrapper is a separate unit. */
__attribute__((noinline, used, noreturn)) void _exit_halt(int status)
{
    (void)status;
    for (;;) {
    }
}

extern void exit_wrapper(int status) __attribute__((noreturn));

void touch_runtime_0164_reset_entry(void)
{
    uint8_t *dst;
    const uint8_t *src;
    size_t n;

    touch_runtime_0158_stack_limit();

    dst = (uint8_t *)&__data_start;
    src = (const uint8_t *)&__data_load_start;
    n = (size_t)((uint8_t *)&__data_end - dst);
    if (n != 0u) {
        (void)memcpy(dst, src, n);
    }

    dst = (uint8_t *)&__bss_start;
    n = (size_t)((uint8_t *)&__bss_end - dst);
    if (n != 0u) {
        (void)memset(dst, 0, n);
    }

    __libc_init_array();
    exit_wrapper(touch_product_09b4_run());
}
