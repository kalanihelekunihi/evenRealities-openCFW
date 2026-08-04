/*
 * This file is derived from the CmBacktrace Library.
 *
 * Copyright (c) 2016-2019, Armink, <armink.ztl@gmail.com>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE.
 *
 * SPDX-License-Identifier: MIT
 *
 * Bounded production adaptation of CmBacktrace's static
 * get_cur_thread_name() FreeRTOS branch. OpenCFW selects upstream commit
 * 73714489f9d8af130aacb515586b397b604a5768, the newest authenticated
 * unmodified state in the G2-compatible interval beginning at
 * 4abadfa0c4f86f22352aa5ab9ebbb4f687125a1c. This is a reproducible
 * compatibility baseline, not a claim that Even used that exact checkout.
 *
 * The official G2 body is [0x00593AF6,0x00593AFE). The external zero-argument
 * seam is deliberately implemented by a separate source adapter preserving
 * the recovered vTaskName current-TCB lookup, including its null-TCB result.
 */

#include "runtime_cmbacktrace_get_cur_thread_name.h"

__attribute__((used, noinline))
const char *open_cfw_cmbacktrace_get_cur_thread_name(void)
{
    return open_cfw_cmbacktrace_pc_task_get_name_current();
}
