/* Clean-room reconstruction of driver/uled/display_preprocess.c. */

#include <stddef.h>
#include <stdint.h>

typedef struct {
    uint32_t control;
    uint32_t dimensions;
    uint32_t stride;
    uint32_t pixel_count;
    uint32_t destination;
    uint32_t destination_alias;
    uint32_t reserved;
} open_cfw_uled_gpu_destination;

typedef struct {
    uint32_t reserved[2];
    uint32_t max_x;
    uint32_t max_y;
} open_cfw_uled_gpu_region;

_Static_assert(sizeof(open_cfw_uled_gpu_destination) == 28,
    "stock GPU destination descriptor must remain twenty-eight bytes");
_Static_assert(sizeof(open_cfw_uled_gpu_region) == 16,
    "stock GPU region descriptor must remain sixteen bytes");

#ifndef OPEN_CFW_ULED_ASSERT
void open_cfw_uled_assert_failure(const char *expression);
#define OPEN_CFW_ULED_ASSERT(condition, expression) \
    do { \
        if (!(condition)) { \
            open_cfw_uled_assert_failure(expression); \
            for (;;) { \
            } \
        } \
    } while (0)
#endif
#ifndef OPEN_CFW_ULED_GPU_START
int open_cfw_uled_gpu_start(
    const open_cfw_uled_gpu_destination *destination,
    const open_cfw_uled_gpu_region *region,
    uint32_t flags
);
#define OPEN_CFW_ULED_GPU_START(destination, region, flags) \
    open_cfw_uled_gpu_start((destination), (region), (flags))
#endif
#ifndef OPEN_CFW_ULED_GPU_DESTINATION_CONFIGURE
void open_cfw_uled_gpu_destination_configure(uint32_t channel, uint32_t enabled);
#define OPEN_CFW_ULED_GPU_DESTINATION_CONFIGURE(channel, enabled) \
    open_cfw_uled_gpu_destination_configure((channel), (enabled))
#endif
#ifndef OPEN_CFW_ULED_GPU_DESTINATION_MODE
void open_cfw_uled_gpu_destination_mode(uint32_t channel);
#define OPEN_CFW_ULED_GPU_DESTINATION_MODE(channel) \
    open_cfw_uled_gpu_destination_mode(channel)
#endif
#ifndef OPEN_CFW_ULED_GPU_DESTINATION_ENABLE
void open_cfw_uled_gpu_destination_enable(uint32_t channel, uint32_t enabled);
#define OPEN_CFW_ULED_GPU_DESTINATION_ENABLE(channel, enabled) \
    open_cfw_uled_gpu_destination_enable((channel), (enabled))
#endif
#ifndef OPEN_CFW_ULED_GPU_SOURCE_CONFIGURE
void open_cfw_uled_gpu_source_configure(
    const void *source,
    uint32_t width_words,
    uint32_t height,
    uint32_t format,
    uint32_t stride_words,
    uint32_t flags
);
#define OPEN_CFW_ULED_GPU_SOURCE_CONFIGURE( \
    source, width, height, format, stride, flags \
) open_cfw_uled_gpu_source_configure( \
    (source), (width), (height), (format), (stride), (flags) \
)
#endif
#ifndef OPEN_CFW_ULED_GPU_OFFSET_CONFIGURE
void open_cfw_uled_gpu_offset_configure(uint32_t x_words, uint32_t y);
#define OPEN_CFW_ULED_GPU_OFFSET_CONFIGURE(x, y) \
    open_cfw_uled_gpu_offset_configure((x), (y))
#endif
#ifndef OPEN_CFW_ULED_GPU_COMMIT
void open_cfw_uled_gpu_commit(uint32_t enabled);
#define OPEN_CFW_ULED_GPU_COMMIT(enabled) open_cfw_uled_gpu_commit(enabled)
#endif
#ifndef OPEN_CFW_ULED_DIAGNOSTIC
#define OPEN_CFW_ULED_DIAGNOSTIC(result) ((void)(result))
#endif

void open_cfw_uled_buffer_sync_to_fb(
    void *destination,
    const void *source,
    uint32_t destination_width,
    uint32_t destination_height,
    uint32_t source_width,
    uint32_t source_height,
    uint32_t offset_x,
    uint32_t offset_y
)
{
    open_cfw_uled_gpu_region region = {{0u, 0u}, 0u, 0u};
    open_cfw_uled_gpu_destination descriptor = {
        0x00000619u, 0u, 0u, 0u, 0u, 0u, 0u,
    };
    uint32_t half_destination_width;
    uint32_t half_source_width;
    int result;

    OPEN_CFW_ULED_ASSERT(destination != NULL, "ptr_des != NULL");
    OPEN_CFW_ULED_ASSERT(source != NULL, "ptr_src != NULL");
    OPEN_CFW_ULED_ASSERT(
        destination_width > source_width, "des_width > src_width"
    );
    OPEN_CFW_ULED_ASSERT(
        destination_height > source_height, "des_hight > src_hight"
    );
    OPEN_CFW_ULED_ASSERT((offset_x & 1u) == 0u, "offset_x % 2 == 0");
    OPEN_CFW_ULED_ASSERT((source_width & 1u) == 0u, "src_width % 2 == 0");
    OPEN_CFW_ULED_ASSERT(
        (destination_width & 1u) == 0u, "des_width % 2 == 0"
    );
    OPEN_CFW_ULED_ASSERT(
        ((uintptr_t)destination & 7u) == 0u,
        "((uint32_t)ptr_des & 0x00000007) == 0"
    );
    OPEN_CFW_ULED_ASSERT(
        ((uintptr_t)source & 7u) == 0u,
        "((uint32_t)ptr_src & 0x00000007) == 0"
    );

    half_destination_width = destination_width >> 1;
    half_source_width = source_width >> 1;
    region.max_x = half_destination_width - 1u;
    region.max_y = destination_height - 1u;
    descriptor.dimensions =
        (half_destination_width & 0xffffu) | (destination_height << 16);
    descriptor.stride = half_destination_width & 0xffffu;
    descriptor.pixel_count = (destination_width * destination_height) >> 1;
    descriptor.destination = (uint32_t)(uintptr_t)destination;
    descriptor.destination_alias = (uint32_t)(uintptr_t)destination;

    result = OPEN_CFW_ULED_GPU_START(&descriptor, &region, 0u);
    if ((uint8_t)result != 1u) {
        OPEN_CFW_ULED_DIAGNOSTIC((uint8_t)result);
        return;
    }

    OPEN_CFW_ULED_GPU_DESTINATION_CONFIGURE(0u, 1u);
    OPEN_CFW_ULED_GPU_DESTINATION_MODE(0u);
    OPEN_CFW_ULED_GPU_DESTINATION_ENABLE(0u, 1u);
    OPEN_CFW_ULED_GPU_SOURCE_CONFIGURE(
        source, half_source_width, source_height, 9u,
        half_source_width, 0u
    );
    OPEN_CFW_ULED_GPU_OFFSET_CONFIGURE(offset_x / 2u, offset_y);
    OPEN_CFW_ULED_GPU_COMMIT(1u);
}
