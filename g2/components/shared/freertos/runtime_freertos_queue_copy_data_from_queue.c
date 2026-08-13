/*
 * FreeRTOS Kernel V10.5.1
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates.
 *
 * SPDX-License-Identifier: MIT
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 * Bounded, freestanding adaptation of private prvCopyDataFromQueue() from
 * authenticated FreeRTOS-Kernel V10.5.1 commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.  The official G2 body is
 * [0x00441F5E,0x00441F88).
 */

#include "runtime_freertos_queue_next_closure.h"

extern void __aeabi_memcpy(void *destination, const void *source,
                           open_cfw_freertos_queue_next_ubase_type size);

__attribute__((used, noinline))
void open_cfw_freertos_queue_copy_data_from_queue(
    struct open_cfw_freertos_queue_next_control *queue,
    void *buffer
)
{
    if (queue->item_size != 0U) {
        queue->value.queue.read_from += queue->item_size;
        if (queue->value.queue.read_from >= queue->value.queue.tail) {
            queue->value.queue.read_from = queue->head;
        }
        __aeabi_memcpy(buffer, queue->value.queue.read_from, queue->item_size);
    }
}
