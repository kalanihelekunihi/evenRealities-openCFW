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
 * Bounded, freestanding port of vListInitialise() from FreeRTOS-Kernel
 * V10.5.1 list.c at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.
 *
 * The official G2 image places this complete leaf at
 * [0x0045607C, 0x0045609A).  The recovered configuration uses 32-bit
 * UBaseType_t, TickType_t, and pointers,
 * configUSE_MINI_LIST_ITEM=1,
 * configUSE_LIST_DATA_INTEGRITY_CHECK_BYTES=0, and
 * portMAX_DELAY=0xFFFFFFFF.
 */

typedef unsigned int open_cfw_freertos_list_initialise_ubase_type;
typedef unsigned int open_cfw_freertos_list_initialise_tick_type;

struct open_cfw_freertos_list_initialise_list;

struct open_cfw_freertos_list_initialise_item {
    open_cfw_freertos_list_initialise_tick_type item_value;
    struct open_cfw_freertos_list_initialise_item *next;
    struct open_cfw_freertos_list_initialise_item *previous;
    void *owner;
    struct open_cfw_freertos_list_initialise_list *container;
};

struct open_cfw_freertos_list_initialise_mini_item {
    open_cfw_freertos_list_initialise_tick_type item_value;
    struct open_cfw_freertos_list_initialise_item *next;
    struct open_cfw_freertos_list_initialise_item *previous;
};

struct open_cfw_freertos_list_initialise_list {
    volatile open_cfw_freertos_list_initialise_ubase_type item_count;
    struct open_cfw_freertos_list_initialise_item *index;
    struct open_cfw_freertos_list_initialise_mini_item end;
};

#if defined(__arm__)
_Static_assert(sizeof(void *) == 4U, "Apollo510 requires 32-bit pointers");
_Static_assert(
    sizeof(open_cfw_freertos_list_initialise_ubase_type) == 4U,
    "FreeRTOS UBaseType_t width changed"
);
_Static_assert(
    sizeof(open_cfw_freertos_list_initialise_tick_type) == 4U,
    "FreeRTOS TickType_t width changed"
);
_Static_assert(
    sizeof(struct open_cfw_freertos_list_initialise_item) == 0x14U,
    "FreeRTOS ListItem_t ABI changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_list_initialise_item,
        next
    ) == 0x04U,
    "ListItem_t next offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_list_initialise_item,
        previous
    ) == 0x08U,
    "ListItem_t previous offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_list_initialise_item,
        container
    ) == 0x10U,
    "ListItem_t container offset changed"
);
_Static_assert(
    sizeof(struct open_cfw_freertos_list_initialise_mini_item) == 0x0CU,
    "FreeRTOS MiniListItem_t ABI changed"
);
_Static_assert(
    sizeof(struct open_cfw_freertos_list_initialise_list) == 0x14U,
    "FreeRTOS List_t ABI changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_list_initialise_list,
        item_count
    ) == 0x00U,
    "List_t item-count offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_list_initialise_list,
        index
    ) == 0x04U,
    "List_t index offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_list_initialise_list,
        end
    ) == 0x08U,
    "List_t end-marker offset changed"
);
#endif

__attribute__((used, noinline))
void open_cfw_freertos_list_initialise(
    struct open_cfw_freertos_list_initialise_list *list
)
{
    struct open_cfw_freertos_list_initialise_item *end =
        (struct open_cfw_freertos_list_initialise_item *)(void *)&list->end;

    list->index = end;
    list->end.item_value =
        (open_cfw_freertos_list_initialise_tick_type)0xFFFFFFFFU;
    list->end.next = end;
    list->end.previous = end;
    list->item_count =
        (open_cfw_freertos_list_initialise_ubase_type)0U;
}
