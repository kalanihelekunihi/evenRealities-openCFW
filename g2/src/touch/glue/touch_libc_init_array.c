/*
 * Copyright (C) 2004 CodeSourcery, LLC
 *
 * Permission to use, copy, modify, and distribute this file
 * for any purpose is hereby granted without fee, provided that
 * the above copyright notice and this notice appears in all
 * copies.
 *
 * This file is distributed WITHOUT ANY WARRANTY; without even the implied
 * warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 *
 * Adapted for the G2 touch source build from newlib's init-array loop.
 */
#include <stddef.h>

typedef void (*touch_init_hook)(void);

extern touch_init_hook __preinit_array_start[] __attribute__((weak));
extern touch_init_hook __preinit_array_end[] __attribute__((weak));
extern touch_init_hook __init_array_start[] __attribute__((weak));
extern touch_init_hook __init_array_end[] __attribute__((weak));
extern void _init(void);

void __libc_init_array(void)
{
    size_t count;
    size_t i;

    count = __preinit_array_end - __preinit_array_start;
    for (i = 0; i < count; i++)
        __preinit_array_start[i]();

    _init();

    count = __init_array_end - __init_array_start;
    for (i = 0; i < count; i++)
        __init_array_start[i]();
}
