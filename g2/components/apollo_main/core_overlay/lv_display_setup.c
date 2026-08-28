/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacement for the G2 2.2.6.10 LVGL display setup routine at
 * 0x00473782.
 */

typedef void *(*open_cfw_lv_display_setup_allocate_fn)(unsigned int size);
typedef unsigned int (*open_cfw_lv_display_setup_get_fn)(void);
typedef unsigned char (*open_cfw_lv_display_setup_configure_fn)(
    void *state,
    unsigned int width,
    unsigned int height,
    unsigned int format,
    unsigned int flags,
    unsigned int configuration,
    unsigned int bytes
);
typedef void (*open_cfw_lv_display_setup_log_fn)(
    unsigned int level,
    const void *file,
    unsigned int line,
    const void *function,
    ...
);
typedef void *(*open_cfw_lv_display_setup_create_fn)(
    unsigned int width,
    unsigned int height
);
typedef void (*open_cfw_lv_display_setup_pair_fn)(
    void *object,
    const void *value
);
typedef void *(*open_cfw_lv_display_setup_buffer_create_fn)(
    unsigned int width,
    unsigned int height,
    unsigned int format,
    unsigned int flags
);
typedef void (*open_cfw_lv_display_setup_attach_fn)(
    void *object,
    void *buffer,
    unsigned int layer
);
typedef void (*open_cfw_lv_display_setup_value_fn)(
    void *object,
    unsigned int value
);
typedef void (*open_cfw_lv_display_setup_pair_u32_fn)(
    void *object,
    unsigned int first,
    unsigned int second
);

#ifndef OPEN_CFW_LV_DISPLAY_SETUP_STATE
#define OPEN_CFW_LV_DISPLAY_SETUP_STATE \
    (*(void * volatile *)(void *)0x200746B8U)
#endif

#ifndef OPEN_CFW_LV_DISPLAY_SETUP_BUFFER
#define OPEN_CFW_LV_DISPLAY_SETUP_BUFFER \
    (*(void * volatile *)(void *)0x200746B4U)
#endif

#ifndef OPEN_CFW_LV_DISPLAY_SETUP_ALLOCATE
#define OPEN_CFW_LV_DISPLAY_SETUP_ALLOCATE(size) \
    (((open_cfw_lv_display_setup_allocate_fn)0x0044F719U)(size))
#endif

#ifndef OPEN_CFW_LV_DISPLAY_SETUP_CONFIGURATION
#define OPEN_CFW_LV_DISPLAY_SETUP_CONFIGURATION() \
    (((open_cfw_lv_display_setup_get_fn)0x0046CA6FU)())
#endif

#ifndef OPEN_CFW_LV_DISPLAY_SETUP_CONFIGURE
#define OPEN_CFW_LV_DISPLAY_SETUP_CONFIGURE( \
    state, width, height, format, flags, configuration, bytes \
) \
    (((open_cfw_lv_display_setup_configure_fn)0x0048AEF9U)( \
        (state), \
        (width), \
        (height), \
        (format), \
        (flags), \
        (configuration), \
        (bytes) \
    ))
#endif

#ifndef OPEN_CFW_LV_DISPLAY_SETUP_LOG
#define OPEN_CFW_LV_DISPLAY_SETUP_LOG \
    ((open_cfw_lv_display_setup_log_fn)0x0044D25DU)
#endif

#ifndef OPEN_CFW_LV_DISPLAY_SETUP_CREATE
#define OPEN_CFW_LV_DISPLAY_SETUP_CREATE(width, height) \
    (((open_cfw_lv_display_setup_create_fn)0x0044F7C1U)( \
        (width), \
        (height) \
    ))
#endif

#ifndef OPEN_CFW_LV_DISPLAY_SETUP_CALLBACK
#define OPEN_CFW_LV_DISPLAY_SETUP_CALLBACK ((const void *)0x004736F5U)
#endif

#ifndef OPEN_CFW_LV_DISPLAY_SETUP_REGISTER
#define OPEN_CFW_LV_DISPLAY_SETUP_REGISTER(object, callback) \
    (((open_cfw_lv_display_setup_pair_fn)0x0044FC2FU)( \
        (object), \
        (callback) \
    ))
#endif

#ifndef OPEN_CFW_LV_DISPLAY_SETUP_BUFFER_CREATE
#define OPEN_CFW_LV_DISPLAY_SETUP_BUFFER_CREATE(width, height, format, flags) \
    (((open_cfw_lv_display_setup_buffer_create_fn)0x0048AFFBU)( \
        (width), \
        (height), \
        (format), \
        (flags) \
    ))
#endif

#ifndef OPEN_CFW_LV_DISPLAY_SETUP_ATTACH
#define OPEN_CFW_LV_DISPLAY_SETUP_ATTACH(object, buffer, layer) \
    (((open_cfw_lv_display_setup_attach_fn)0x0044FBFDU)( \
        (object), \
        (buffer), \
        (layer) \
    ))
#endif

#ifndef OPEN_CFW_LV_DISPLAY_SETUP_MODE
#define OPEN_CFW_LV_DISPLAY_SETUP_MODE(object, value) \
    (((open_cfw_lv_display_setup_value_fn)0x0044FC19U)( \
        (object), \
        (value) \
    ))
#endif

#ifndef OPEN_CFW_LV_DISPLAY_SETUP_SIZE
#define OPEN_CFW_LV_DISPLAY_SETUP_SIZE(object, width, height) \
    (((open_cfw_lv_display_setup_pair_u32_fn)0x0044FA3FU)( \
        (object), \
        (width), \
        (height) \
    ))
#endif

#ifndef OPEN_CFW_LV_DISPLAY_SETUP_POSITION
#define OPEN_CFW_LV_DISPLAY_SETUP_POSITION(object, x, y) \
    (((open_cfw_lv_display_setup_pair_u32_fn)0x0044FA5FU)( \
        (object), \
        (x), \
        (y) \
    ))
#endif

#define OPEN_CFW_LV_DISPLAY_SETUP_FILE ((const void *)0x006DD7D4U)
#define OPEN_CFW_LV_DISPLAY_SETUP_FUNCTION ((const void *)0x0077F950U)
#define OPEN_CFW_LV_DISPLAY_SETUP_ERROR ((const void *)0x00760650U)

__attribute__((used, noinline))
void open_cfw_lv_display_setup(void)
{
    void *state = OPEN_CFW_LV_DISPLAY_SETUP_ALLOCATE(0x1CU);
    unsigned int configuration;
    void *object;
    void *buffer;

    OPEN_CFW_LV_DISPLAY_SETUP_STATE = state;
    configuration = OPEN_CFW_LV_DISPLAY_SETUP_CONFIGURATION();
    if (
        OPEN_CFW_LV_DISPLAY_SETUP_CONFIGURE(
            state,
            0x240U,
            0x120U,
            0xDU,
            0U,
            configuration,
            0x14400U
        ) == 0U
    ) {
        OPEN_CFW_LV_DISPLAY_SETUP_LOG(
            3U,
            OPEN_CFW_LV_DISPLAY_SETUP_FILE,
            0x105U,
            OPEN_CFW_LV_DISPLAY_SETUP_FUNCTION,
            OPEN_CFW_LV_DISPLAY_SETUP_ERROR
        );
        return;
    }

    object = OPEN_CFW_LV_DISPLAY_SETUP_CREATE(0x240U, 0x120U);
    OPEN_CFW_LV_DISPLAY_SETUP_REGISTER(
        object,
        OPEN_CFW_LV_DISPLAY_SETUP_CALLBACK
    );
    buffer = OPEN_CFW_LV_DISPLAY_SETUP_BUFFER_CREATE(
        0x240U,
        0x120U,
        6U,
        0U
    );
    OPEN_CFW_LV_DISPLAY_SETUP_BUFFER = buffer;
    OPEN_CFW_LV_DISPLAY_SETUP_ATTACH(object, buffer, 0U);
    OPEN_CFW_LV_DISPLAY_SETUP_MODE(object, 1U);
    OPEN_CFW_LV_DISPLAY_SETUP_SIZE(object, 0x240U, 0x120U);
    OPEN_CFW_LV_DISPLAY_SETUP_POSITION(object, 0U, 0U);
}

#undef OPEN_CFW_LV_DISPLAY_SETUP_ERROR
#undef OPEN_CFW_LV_DISPLAY_SETUP_FUNCTION
#undef OPEN_CFW_LV_DISPLAY_SETUP_FILE
#undef OPEN_CFW_LV_DISPLAY_SETUP_POSITION
#undef OPEN_CFW_LV_DISPLAY_SETUP_SIZE
#undef OPEN_CFW_LV_DISPLAY_SETUP_MODE
#undef OPEN_CFW_LV_DISPLAY_SETUP_ATTACH
#undef OPEN_CFW_LV_DISPLAY_SETUP_BUFFER_CREATE
#undef OPEN_CFW_LV_DISPLAY_SETUP_REGISTER
#undef OPEN_CFW_LV_DISPLAY_SETUP_CALLBACK
#undef OPEN_CFW_LV_DISPLAY_SETUP_CREATE
#undef OPEN_CFW_LV_DISPLAY_SETUP_LOG
#undef OPEN_CFW_LV_DISPLAY_SETUP_CONFIGURE
#undef OPEN_CFW_LV_DISPLAY_SETUP_CONFIGURATION
#undef OPEN_CFW_LV_DISPLAY_SETUP_ALLOCATE
#undef OPEN_CFW_LV_DISPLAY_SETUP_BUFFER
#undef OPEN_CFW_LV_DISPLAY_SETUP_STATE
