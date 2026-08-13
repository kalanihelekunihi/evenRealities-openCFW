#ifndef OPEN_CFW_RING_BUFFER_ASSERT_H
#define OPEN_CFW_RING_BUFFER_ASSERT_H

void open_cfw_ring_buffer_assert_fail(
    const char *expression,
    const char *file,
    unsigned int line
) __attribute__((noreturn));

#define assert(expression) \
    ((expression) ? (void)0 : open_cfw_ring_buffer_assert_fail( \
        #expression, __FILE__, (unsigned int)__LINE__))

#endif
