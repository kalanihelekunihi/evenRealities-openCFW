/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded G2 production adaptation of AndersKaloer/Ring-Buffer commit
 * 190e30bebcec22d7311fd941179d70b4f439c441. The seven retained functions
 * correspond to stock [0x00598134,0x0059823C); ring_buffer_peek and
 * ring_buffer_num_items are not linked because the official image does not
 * retain those entries.
 */

typedef unsigned int open_cfw_ring_buffer_size;

struct open_cfw_ring_buffer {
    unsigned char *buffer;
    open_cfw_ring_buffer_size buffer_mask;
    open_cfw_ring_buffer_size tail_index;
    open_cfw_ring_buffer_size head_index;
};

#ifndef OPEN_CFW_RING_BUFFER_HOST_TEST
_Static_assert(sizeof(unsigned char *) == 4U, "ring-buffer pointer width changed");
_Static_assert(sizeof(open_cfw_ring_buffer_size) == 4U, "ring-buffer size width changed");
_Static_assert(sizeof(struct open_cfw_ring_buffer) == 16U, "ring-buffer ABI changed");
_Static_assert(__builtin_offsetof(struct open_cfw_ring_buffer, buffer) == 0U, "buffer offset changed");
_Static_assert(__builtin_offsetof(struct open_cfw_ring_buffer, buffer_mask) == 4U, "mask offset changed");
_Static_assert(__builtin_offsetof(struct open_cfw_ring_buffer, tail_index) == 8U, "tail offset changed");
_Static_assert(__builtin_offsetof(struct open_cfw_ring_buffer, head_index) == 12U, "head offset changed");
#endif

#ifndef OPEN_CFW_RING_BUFFER_ASSERT_POWER_OF_TWO
typedef void (*open_cfw_ring_buffer_assert_fn)(
    const char *,
    const char *,
    unsigned int
);
#define OPEN_CFW_RING_BUFFER_ASSERT_POWER_OF_TWO() \
    (((open_cfw_ring_buffer_assert_fn)(__UINTPTR_TYPE__)0x004D09B5U)( \
        (const char *)(__UINTPTR_TYPE__)0x0074D6ECU, \
        (const char *)(__UINTPTR_TYPE__)0x006FC92CU, \
        9U \
    ))
#endif

#if !defined(OPEN_CFW_RING_BUFFER_SELECTION) \
    || OPEN_CFW_RING_BUFFER_SELECTION == 0
__attribute__((used, noinline))
unsigned char open_cfw_ring_buffer_is_empty(
    const struct open_cfw_ring_buffer *ring
)
{
    return (unsigned char)(ring->head_index == ring->tail_index);
}
#else
unsigned char open_cfw_ring_buffer_is_empty(
    const struct open_cfw_ring_buffer *ring
);
#endif

#if !defined(OPEN_CFW_RING_BUFFER_SELECTION) \
    || OPEN_CFW_RING_BUFFER_SELECTION == 1
__attribute__((used, noinline))
unsigned char open_cfw_ring_buffer_is_full(
    const struct open_cfw_ring_buffer *ring
)
{
    return (unsigned char)(
        ((ring->head_index - ring->tail_index) & ring->buffer_mask)
            == ring->buffer_mask
    );
}
#else
unsigned char open_cfw_ring_buffer_is_full(
    const struct open_cfw_ring_buffer *ring
);
#endif

#if !defined(OPEN_CFW_RING_BUFFER_SELECTION) \
    || OPEN_CFW_RING_BUFFER_SELECTION == 2
__attribute__((used, noinline))
void open_cfw_ring_buffer_init(
    struct open_cfw_ring_buffer *ring,
    unsigned char *buffer,
    open_cfw_ring_buffer_size buffer_size
)
{
    if ((buffer_size & (buffer_size - 1U)) != 0U) {
        OPEN_CFW_RING_BUFFER_ASSERT_POWER_OF_TWO();
    }
    ring->buffer = buffer;
    ring->buffer_mask = buffer_size - 1U;
    ring->tail_index = 0U;
    ring->head_index = 0U;
}
#endif

#if !defined(OPEN_CFW_RING_BUFFER_SELECTION) \
    || OPEN_CFW_RING_BUFFER_SELECTION == 3
__attribute__((used, noinline))
void open_cfw_ring_buffer_queue(
    struct open_cfw_ring_buffer *ring,
    unsigned char data
)
{
    if (open_cfw_ring_buffer_is_full(ring) != 0U) {
        ring->tail_index = (ring->tail_index + 1U) & ring->buffer_mask;
    }
    ring->buffer[ring->head_index] = data;
    ring->head_index = (ring->head_index + 1U) & ring->buffer_mask;
}
#else
void open_cfw_ring_buffer_queue(
    struct open_cfw_ring_buffer *ring,
    unsigned char data
);
#endif

#if !defined(OPEN_CFW_RING_BUFFER_SELECTION) \
    || OPEN_CFW_RING_BUFFER_SELECTION == 4
__attribute__((used, noinline))
void open_cfw_ring_buffer_queue_arr(
    struct open_cfw_ring_buffer *ring,
    const unsigned char *data,
    open_cfw_ring_buffer_size size
)
{
    open_cfw_ring_buffer_size index;

    for (index = 0U; index < size; index += 1U) {
        open_cfw_ring_buffer_queue(ring, data[index]);
    }
}
#endif

#if !defined(OPEN_CFW_RING_BUFFER_SELECTION) \
    || OPEN_CFW_RING_BUFFER_SELECTION == 5
__attribute__((used, noinline))
unsigned char open_cfw_ring_buffer_dequeue(
    struct open_cfw_ring_buffer *ring,
    unsigned char *data
)
{
    if (open_cfw_ring_buffer_is_empty(ring) != 0U) {
        return 0U;
    }
    *data = ring->buffer[ring->tail_index];
    ring->tail_index = (ring->tail_index + 1U) & ring->buffer_mask;
    return 1U;
}
#else
unsigned char open_cfw_ring_buffer_dequeue(
    struct open_cfw_ring_buffer *ring,
    unsigned char *data
);
#endif

#if !defined(OPEN_CFW_RING_BUFFER_SELECTION) \
    || OPEN_CFW_RING_BUFFER_SELECTION == 6
__attribute__((used, noinline))
open_cfw_ring_buffer_size open_cfw_ring_buffer_dequeue_arr(
    struct open_cfw_ring_buffer *ring,
    unsigned char *data,
    open_cfw_ring_buffer_size length
)
{
    open_cfw_ring_buffer_size count = 0U;

    if (open_cfw_ring_buffer_is_empty(ring) != 0U) {
        return 0U;
    }
    while (
        count < length
            && open_cfw_ring_buffer_dequeue(ring, data + count) != 0U
    ) {
        count += 1U;
    }
    return count;
}
#endif

#undef OPEN_CFW_RING_BUFFER_ASSERT_POWER_OF_TWO
