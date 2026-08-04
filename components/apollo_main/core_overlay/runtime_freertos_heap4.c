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
 * Bounded, freestanding port of the four-function heap_4.c allocator closure
 * from FreeRTOS-Kernel V10.5.1 commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.
 *
 * The official G2 image places the complete stock closure at
 * [0x00456110, 0x00456338).  This adaptation preserves the released
 * pvPortMalloc(), vPortFree(), prvHeapInit(), and
 * prvInsertBlockIntoFreeList() algorithms while binding the recovered G2
 * heap, compatibility globals, scheduler lock, malloc-failed hook, and
 * source-owned interrupt-mask assertion path explicitly.
 */

typedef unsigned char open_cfw_freertos_heap4_u8;
typedef unsigned int open_cfw_freertos_heap4_size;
typedef __UINTPTR_TYPE__ open_cfw_freertos_heap4_uintptr;

struct open_cfw_freertos_heap4_block {
    struct open_cfw_freertos_heap4_block *next_free_block;
    open_cfw_freertos_heap4_size block_size;
};

enum {
    OPEN_CFW_FREERTOS_HEAP4_TOTAL_HEAP_SIZE = 0x0002F000U,
    OPEN_CFW_FREERTOS_HEAP4_ALIGNMENT = 8U,
    OPEN_CFW_FREERTOS_HEAP4_ALIGNMENT_MASK = 7U,
    OPEN_CFW_FREERTOS_HEAP4_ALLOCATED_BIT = 0x80000000U
};

#if defined(__arm__)
_Static_assert(sizeof(void *) == 4U, "Apollo510 requires 32-bit pointers");
_Static_assert(
    sizeof(open_cfw_freertos_heap4_size) == 4U,
    "FreeRTOS heap size type width changed"
);
_Static_assert(
    sizeof(struct open_cfw_freertos_heap4_block) == 8U,
    "FreeRTOS heap_4 BlockLink_t ABI changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_heap4_block,
        next_free_block
    ) == 0U,
    "FreeRTOS heap_4 next-link offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_heap4_block,
        block_size
    ) == 4U,
    "FreeRTOS heap_4 size offset changed"
);
#endif

#ifndef OPEN_CFW_FREERTOS_HEAP4_HEAP_ADDRESS
#define OPEN_CFW_FREERTOS_HEAP4_HEAP_ADDRESS 0x20004558U
#endif

#ifndef OPEN_CFW_FREERTOS_HEAP4_START_ADDRESS
#define OPEN_CFW_FREERTOS_HEAP4_START_ADDRESS 0x20074158U
#endif

#ifndef OPEN_CFW_FREERTOS_HEAP4_END_POINTER_ADDRESS
#define OPEN_CFW_FREERTOS_HEAP4_END_POINTER_ADDRESS 0x2007465CU
#endif

#ifndef OPEN_CFW_FREERTOS_HEAP4_FREE_BYTES_ADDRESS
#define OPEN_CFW_FREERTOS_HEAP4_FREE_BYTES_ADDRESS 0x20074660U
#endif

#ifndef OPEN_CFW_FREERTOS_HEAP4_MINIMUM_BYTES_ADDRESS
#define OPEN_CFW_FREERTOS_HEAP4_MINIMUM_BYTES_ADDRESS 0x20074664U
#endif

#ifndef OPEN_CFW_FREERTOS_HEAP4_ALLOCATION_COUNT_ADDRESS
#define OPEN_CFW_FREERTOS_HEAP4_ALLOCATION_COUNT_ADDRESS 0x20074668U
#endif

#ifndef OPEN_CFW_FREERTOS_HEAP4_FREE_COUNT_ADDRESS
#define OPEN_CFW_FREERTOS_HEAP4_FREE_COUNT_ADDRESS 0x2007466CU
#endif

#define OPEN_CFW_FREERTOS_HEAP4_AT(type, address) \
    (*(type *)(open_cfw_freertos_heap4_uintptr)(address))

#define OPEN_CFW_FREERTOS_HEAP4_HEAP \
    ((open_cfw_freertos_heap4_u8 *)(open_cfw_freertos_heap4_uintptr) \
        OPEN_CFW_FREERTOS_HEAP4_HEAP_ADDRESS)

#define OPEN_CFW_FREERTOS_HEAP4_START \
    OPEN_CFW_FREERTOS_HEAP4_AT( \
        struct open_cfw_freertos_heap4_block, \
        OPEN_CFW_FREERTOS_HEAP4_START_ADDRESS \
    )

#define OPEN_CFW_FREERTOS_HEAP4_END \
    OPEN_CFW_FREERTOS_HEAP4_AT( \
        struct open_cfw_freertos_heap4_block *, \
        OPEN_CFW_FREERTOS_HEAP4_END_POINTER_ADDRESS \
    )

#define OPEN_CFW_FREERTOS_HEAP4_FREE_BYTES \
    OPEN_CFW_FREERTOS_HEAP4_AT( \
        open_cfw_freertos_heap4_size, \
        OPEN_CFW_FREERTOS_HEAP4_FREE_BYTES_ADDRESS \
    )

#define OPEN_CFW_FREERTOS_HEAP4_MINIMUM_BYTES \
    OPEN_CFW_FREERTOS_HEAP4_AT( \
        open_cfw_freertos_heap4_size, \
        OPEN_CFW_FREERTOS_HEAP4_MINIMUM_BYTES_ADDRESS \
    )

#define OPEN_CFW_FREERTOS_HEAP4_ALLOCATION_COUNT \
    OPEN_CFW_FREERTOS_HEAP4_AT( \
        open_cfw_freertos_heap4_size, \
        OPEN_CFW_FREERTOS_HEAP4_ALLOCATION_COUNT_ADDRESS \
    )

#define OPEN_CFW_FREERTOS_HEAP4_FREE_COUNT \
    OPEN_CFW_FREERTOS_HEAP4_AT( \
        open_cfw_freertos_heap4_size, \
        OPEN_CFW_FREERTOS_HEAP4_FREE_COUNT_ADDRESS \
    )

#ifndef OPEN_CFW_FREERTOS_HEAP4_SUSPEND_ALL
#define OPEN_CFW_FREERTOS_HEAP4_SUSPEND_ALL() \
    (((void (*)(void))(open_cfw_freertos_heap4_uintptr)0x00454D7DU)())
#endif

#ifndef OPEN_CFW_FREERTOS_HEAP4_RESUME_ALL
#define OPEN_CFW_FREERTOS_HEAP4_RESUME_ALL() \
    ((void)((unsigned int (*)(void)) \
        (open_cfw_freertos_heap4_uintptr)0x00454DCDU)())
#endif

#ifndef OPEN_CFW_FREERTOS_HEAP4_MALLOC_FAILED
#define OPEN_CFW_FREERTOS_HEAP4_MALLOC_FAILED() \
    (((void (*)(void))(open_cfw_freertos_heap4_uintptr)0x0046D85FU)())
#endif

#ifndef OPEN_CFW_FREERTOS_HEAP4_ASSERT
extern unsigned int ulSetInterruptMask(void);
#define OPEN_CFW_FREERTOS_HEAP4_ASSERT(condition) \
    do { \
        if (!(condition)) { \
            (void)ulSetInterruptMask(); \
            *(volatile unsigned int *) \
                (open_cfw_freertos_heap4_uintptr)0xFFFFFFFFU = 0U; \
            for (;;) { \
                __asm__ volatile("" ::: "memory"); \
            } \
        } \
    } while (0)
#endif

#define OPEN_CFW_FREERTOS_HEAP4_STRUCT_SIZE \
    ((open_cfw_freertos_heap4_size)( \
        sizeof(struct open_cfw_freertos_heap4_block) + \
        (OPEN_CFW_FREERTOS_HEAP4_ALIGNMENT - 1U) \
    ) & ~(open_cfw_freertos_heap4_size) \
        OPEN_CFW_FREERTOS_HEAP4_ALIGNMENT_MASK)

#define OPEN_CFW_FREERTOS_HEAP4_MINIMUM_BLOCK_SIZE \
    ((open_cfw_freertos_heap4_size)( \
        OPEN_CFW_FREERTOS_HEAP4_STRUCT_SIZE << 1U \
    ))

#define OPEN_CFW_FREERTOS_HEAP4_ADD_WILL_OVERFLOW(a, b) \
    ((a) > ((open_cfw_freertos_heap4_size)~0U - (b)))

#define OPEN_CFW_FREERTOS_HEAP4_BLOCK_SIZE_IS_VALID(size) \
    (((size) & OPEN_CFW_FREERTOS_HEAP4_ALLOCATED_BIT) == 0U)

#define OPEN_CFW_FREERTOS_HEAP4_BLOCK_IS_ALLOCATED(block) \
    (((block)->block_size & OPEN_CFW_FREERTOS_HEAP4_ALLOCATED_BIT) != 0U)

#define OPEN_CFW_FREERTOS_HEAP4_ALLOCATE_BLOCK(block) \
    ((block)->block_size |= OPEN_CFW_FREERTOS_HEAP4_ALLOCATED_BIT)

#define OPEN_CFW_FREERTOS_HEAP4_RELEASE_BLOCK(block) \
    ((block)->block_size &= ~OPEN_CFW_FREERTOS_HEAP4_ALLOCATED_BIT)

__attribute__((used, noinline))
void open_cfw_freertos_heap4_init(void);

__attribute__((used, noinline))
void open_cfw_freertos_heap4_insert_free_block(
    struct open_cfw_freertos_heap4_block *block_to_insert
);

/*
 * Exact V10.5.1 pvPortMalloc algorithm.  The narrower project-prefixed
 * signature is the recovered G2 32-bit size_t ABI.
 */
#if !defined(OPEN_CFW_FREERTOS_HEAP4_BUILD_LEAF) || \
    defined(OPEN_CFW_FREERTOS_HEAP4_BUILD_MALLOC)
__attribute__((used, noinline))
void *open_cfw_freertos_heap4_malloc(
    open_cfw_freertos_heap4_size wanted_size
)
{
    struct open_cfw_freertos_heap4_block *block;
    struct open_cfw_freertos_heap4_block *previous_block;
    struct open_cfw_freertos_heap4_block *new_block;
    void *result = (void *)0;
    open_cfw_freertos_heap4_size additional_required_size;

    OPEN_CFW_FREERTOS_HEAP4_SUSPEND_ALL();
    {
        if (OPEN_CFW_FREERTOS_HEAP4_END == (void *)0) {
            open_cfw_freertos_heap4_init();
        }

        if (wanted_size > 0U) {
            additional_required_size =
                OPEN_CFW_FREERTOS_HEAP4_STRUCT_SIZE +
                OPEN_CFW_FREERTOS_HEAP4_ALIGNMENT -
                (wanted_size & OPEN_CFW_FREERTOS_HEAP4_ALIGNMENT_MASK);

            if (!OPEN_CFW_FREERTOS_HEAP4_ADD_WILL_OVERFLOW(
                    wanted_size,
                    additional_required_size
                )) {
                wanted_size += additional_required_size;
            } else {
                wanted_size = 0U;
            }
        }

        if (OPEN_CFW_FREERTOS_HEAP4_BLOCK_SIZE_IS_VALID(wanted_size)) {
            if (
                wanted_size > 0U &&
                wanted_size <= OPEN_CFW_FREERTOS_HEAP4_FREE_BYTES
            ) {
                previous_block = &OPEN_CFW_FREERTOS_HEAP4_START;
                block = OPEN_CFW_FREERTOS_HEAP4_START.next_free_block;

                while (
                    block->block_size < wanted_size &&
                    block->next_free_block != (void *)0
                ) {
                    previous_block = block;
                    block = block->next_free_block;
                }

                if (block != OPEN_CFW_FREERTOS_HEAP4_END) {
                    result = (void *)((
                        (open_cfw_freertos_heap4_u8 *)
                            previous_block->next_free_block
                    ) + OPEN_CFW_FREERTOS_HEAP4_STRUCT_SIZE);

                    previous_block->next_free_block =
                        block->next_free_block;

                    if (
                        (block->block_size - wanted_size) >
                        OPEN_CFW_FREERTOS_HEAP4_MINIMUM_BLOCK_SIZE
                    ) {
                        new_block = (void *)((
                            (open_cfw_freertos_heap4_u8 *)block
                        ) + wanted_size);
                        OPEN_CFW_FREERTOS_HEAP4_ASSERT(
                            (
                                (open_cfw_freertos_heap4_uintptr)new_block &
                                OPEN_CFW_FREERTOS_HEAP4_ALIGNMENT_MASK
                            ) == 0U
                        );

                        new_block->block_size =
                            block->block_size - wanted_size;
                        block->block_size = wanted_size;
                        open_cfw_freertos_heap4_insert_free_block(new_block);
                    }

                    OPEN_CFW_FREERTOS_HEAP4_FREE_BYTES -=
                        block->block_size;

                    if (
                        OPEN_CFW_FREERTOS_HEAP4_FREE_BYTES <
                        OPEN_CFW_FREERTOS_HEAP4_MINIMUM_BYTES
                    ) {
                        OPEN_CFW_FREERTOS_HEAP4_MINIMUM_BYTES =
                            OPEN_CFW_FREERTOS_HEAP4_FREE_BYTES;
                    }

                    OPEN_CFW_FREERTOS_HEAP4_ALLOCATE_BLOCK(block);
                    block->next_free_block = (void *)0;
                    OPEN_CFW_FREERTOS_HEAP4_ALLOCATION_COUNT++;
                }
            }
        }
    }
    OPEN_CFW_FREERTOS_HEAP4_RESUME_ALL();

    if (result == (void *)0) {
        OPEN_CFW_FREERTOS_HEAP4_MALLOC_FAILED();
    }

    OPEN_CFW_FREERTOS_HEAP4_ASSERT(
        (
            (open_cfw_freertos_heap4_uintptr)result &
            OPEN_CFW_FREERTOS_HEAP4_ALIGNMENT_MASK
        ) == 0U
    );
    return result;
}
#endif

/* Exact V10.5.1 vPortFree algorithm; memory clearing is disabled on G2. */
#if !defined(OPEN_CFW_FREERTOS_HEAP4_BUILD_LEAF) || \
    defined(OPEN_CFW_FREERTOS_HEAP4_BUILD_FREE)
__attribute__((used, noinline))
void open_cfw_freertos_heap4_free(void *memory)
{
    open_cfw_freertos_heap4_u8 *bytes =
        (open_cfw_freertos_heap4_u8 *)memory;
    struct open_cfw_freertos_heap4_block *link;

    if (memory != (void *)0) {
        bytes -= OPEN_CFW_FREERTOS_HEAP4_STRUCT_SIZE;
        link = (void *)bytes;

        OPEN_CFW_FREERTOS_HEAP4_ASSERT(
            OPEN_CFW_FREERTOS_HEAP4_BLOCK_IS_ALLOCATED(link)
        );
        OPEN_CFW_FREERTOS_HEAP4_ASSERT(
            link->next_free_block == (void *)0
        );

        if (OPEN_CFW_FREERTOS_HEAP4_BLOCK_IS_ALLOCATED(link)) {
            if (link->next_free_block == (void *)0) {
                OPEN_CFW_FREERTOS_HEAP4_RELEASE_BLOCK(link);

                OPEN_CFW_FREERTOS_HEAP4_SUSPEND_ALL();
                {
                    OPEN_CFW_FREERTOS_HEAP4_FREE_BYTES +=
                        link->block_size;
                    open_cfw_freertos_heap4_insert_free_block(link);
                    OPEN_CFW_FREERTOS_HEAP4_FREE_COUNT++;
                }
                OPEN_CFW_FREERTOS_HEAP4_RESUME_ALL();
            }
        }
    }
}
#endif

/* Exact V10.5.1 prvHeapInit algorithm with the recovered fixed heap. */
#if !defined(OPEN_CFW_FREERTOS_HEAP4_BUILD_LEAF) || \
    defined(OPEN_CFW_FREERTOS_HEAP4_BUILD_INIT)
__attribute__((used, noinline))
void open_cfw_freertos_heap4_init(void)
{
    struct open_cfw_freertos_heap4_block *first_free_block;
    open_cfw_freertos_heap4_u8 *aligned_heap;
    open_cfw_freertos_heap4_uintptr address;
    open_cfw_freertos_heap4_size total_heap_size =
        OPEN_CFW_FREERTOS_HEAP4_TOTAL_HEAP_SIZE;

    address =
        (open_cfw_freertos_heap4_uintptr)OPEN_CFW_FREERTOS_HEAP4_HEAP;

    if (
        (address & OPEN_CFW_FREERTOS_HEAP4_ALIGNMENT_MASK) != 0U
    ) {
        open_cfw_freertos_heap4_uintptr original_address = address;

        address += OPEN_CFW_FREERTOS_HEAP4_ALIGNMENT - 1U;
        address &=
            ~(open_cfw_freertos_heap4_uintptr)
                OPEN_CFW_FREERTOS_HEAP4_ALIGNMENT_MASK;
        total_heap_size -=
            (open_cfw_freertos_heap4_size)(address - original_address);
    }

    aligned_heap = (open_cfw_freertos_heap4_u8 *)address;

    OPEN_CFW_FREERTOS_HEAP4_START.next_free_block =
        (void *)aligned_heap;
    OPEN_CFW_FREERTOS_HEAP4_START.block_size = 0U;

    address =
        (open_cfw_freertos_heap4_uintptr)aligned_heap + total_heap_size;
    address -= OPEN_CFW_FREERTOS_HEAP4_STRUCT_SIZE;
    address &=
        ~(open_cfw_freertos_heap4_uintptr)
            OPEN_CFW_FREERTOS_HEAP4_ALIGNMENT_MASK;
    OPEN_CFW_FREERTOS_HEAP4_END =
        (struct open_cfw_freertos_heap4_block *)address;
    OPEN_CFW_FREERTOS_HEAP4_END->block_size = 0U;
    OPEN_CFW_FREERTOS_HEAP4_END->next_free_block = (void *)0;

    first_free_block =
        (struct open_cfw_freertos_heap4_block *)(void *)aligned_heap;
    first_free_block->block_size =
        (open_cfw_freertos_heap4_size)(
            address -
            (open_cfw_freertos_heap4_uintptr)first_free_block
        );
    first_free_block->next_free_block =
        OPEN_CFW_FREERTOS_HEAP4_END;

    OPEN_CFW_FREERTOS_HEAP4_MINIMUM_BYTES =
        first_free_block->block_size;
    OPEN_CFW_FREERTOS_HEAP4_FREE_BYTES =
        first_free_block->block_size;
}
#endif

/*
 * Exact V10.5.1 prvInsertBlockIntoFreeList algorithm: address-sorted
 * insertion followed by backward and forward adjacency coalescing.
 */
#if !defined(OPEN_CFW_FREERTOS_HEAP4_BUILD_LEAF) || \
    defined(OPEN_CFW_FREERTOS_HEAP4_BUILD_INSERT)
__attribute__((used, noinline))
void open_cfw_freertos_heap4_insert_free_block(
    struct open_cfw_freertos_heap4_block *block_to_insert
)
{
    struct open_cfw_freertos_heap4_block *iterator;
    open_cfw_freertos_heap4_u8 *bytes;

    for (
        iterator = &OPEN_CFW_FREERTOS_HEAP4_START;
        iterator->next_free_block < block_to_insert;
        iterator = iterator->next_free_block
    ) {
    }

    bytes = (open_cfw_freertos_heap4_u8 *)iterator;

    if (
        (bytes + iterator->block_size) ==
        (open_cfw_freertos_heap4_u8 *)block_to_insert
    ) {
        iterator->block_size += block_to_insert->block_size;
        block_to_insert = iterator;
    }

    bytes = (open_cfw_freertos_heap4_u8 *)block_to_insert;

    if (
        (bytes + block_to_insert->block_size) ==
        (open_cfw_freertos_heap4_u8 *)iterator->next_free_block
    ) {
        if (
            iterator->next_free_block !=
            OPEN_CFW_FREERTOS_HEAP4_END
        ) {
            block_to_insert->block_size +=
                iterator->next_free_block->block_size;
            block_to_insert->next_free_block =
                iterator->next_free_block->next_free_block;
        } else {
            block_to_insert->next_free_block =
                OPEN_CFW_FREERTOS_HEAP4_END;
        }
    } else {
        block_to_insert->next_free_block =
            iterator->next_free_block;
    }

    if (iterator != block_to_insert) {
        iterator->next_free_block = block_to_insert;
    }
}
#endif
