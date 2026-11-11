/* SPDX-License-Identifier: GPL-3.0-or-later WITH GCC-exception-3.1
 * Adapted from GCC libgcc/crtstuff.c (FSF copyright 1991-2024).
 * Touch GCC 14.2 crtbegin behavior. The locked image has an empty TM clone
 * table and no frame registration provider, but retains these CRT paths.
 * Evidence: g2/docs/reference/findings-touch-case.md and the pinned
 * crtbegin.o in g2/analysis/touch-crtstuff-source-rebuild-2026-10-09/.
 */
#include <stddef.h>
#include <stdint.h>

typedef void (*touch_crt_function)(void);
extern touch_crt_function __TMC_END__[];
static touch_crt_function __TMC_LIST__[]
    __attribute__((used, section(".tm_clone_table"), aligned(4))) = {};
static const char __EH_FRAME_BEGIN__[]
    __attribute__((section(".eh_frame"), aligned(4))) = {};

extern void _ITM_deregisterTMCloneTable(void *) __attribute__((weak));
extern void _ITM_registerTMCloneTable(void *, size_t) __attribute__((weak));
extern void __deregister_frame_info(const void *) __attribute__((weak));
extern void __register_frame_info(const void *, void *) __attribute__((weak));

__attribute__((noinline)) static void deregister_tm_clones(void)
{
    touch_crt_function *end = __TMC_END__;
    __asm ("" : "+g" (end));
    if (__TMC_LIST__ == end) return;
    void (*fn)(void *) = _ITM_deregisterTMCloneTable;
    __asm ("" : "+r" (fn));
    if (fn) fn(__TMC_LIST__);
}

__attribute__((noinline)) static void register_tm_clones(void)
{
    touch_crt_function *end = __TMC_END__;
    __asm ("" : "+g" (end));
    size_t size = (end - __TMC_LIST__) / 2;
    if (size == 0) return;
    void (*fn)(void *, size_t) = _ITM_registerTMCloneTable;
    __asm ("" : "+r" (fn));
    if (fn) fn(__TMC_LIST__, size);
}

__attribute__((used, section(".touch_bss.crt_completed"))) static _Bool completed;
__attribute__((used, section(".touch_bss.crt_object"))) static uint32_t object[6];

__attribute__((used)) void __do_global_dtors_aux(void)
{
    if (__builtin_expect(completed, 0)) return;
    deregister_tm_clones();
    if (__deregister_frame_info) __deregister_frame_info(__EH_FRAME_BEGIN__);
    completed = 1;
}

__attribute__((used)) void frame_dummy(void)
{
    if (__register_frame_info) __register_frame_info(__EH_FRAME_BEGIN__, object);
    register_tm_clones();
}
