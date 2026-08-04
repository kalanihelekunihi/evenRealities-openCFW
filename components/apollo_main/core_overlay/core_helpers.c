/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Small stock-function replacements for the Even Realities G2 2.2.6.10
 * Apollo510B application. The behavioral specifications and exact function
 * boundaries are recorded in EVIDENCE.md.
 */

#define LENS_SIDE_STATE (*(volatile unsigned char *)0x20075024U)

typedef void (*delay_ms_fn)(unsigned int milliseconds);
typedef unsigned int (*log_flags_fn)(void);
typedef void (*log_record_fn)(
    unsigned int level,
    const void *module,
    const void *file,
    const void *tag,
    unsigned int line,
    const void *format,
    ...
);
typedef void (*trace_record_fn)(
    unsigned int mask,
    const void *schema,
    const void *format,
    ...
);

#define STOCK_DELAY_MS ((delay_ms_fn)0x004910F5U)
#define STOCK_LOG_FLAGS ((log_flags_fn)0x0043D0CFU)
#define STOCK_LOG_RECORD ((log_record_fn)0x0043D575U)
#define STOCK_TRACE_RECORD ((trace_record_fn)0x0043CE9FU)

#define LENS_GPIO_CONFIGURATION \
    (*(volatile unsigned int *)0x0078EE44U)

#define LOG_MODULE ((const void *)0x0077C07CU)
#define LOG_FILE ((const void *)0x00705FB8U)
#define LOG_TAG ((const void *)0x00765790U)
#define LOG_READ_ERROR ((const void *)0x0075A5A8U)
#define TRACE_READ_ERROR ((const void *)0x00718E8CU)
#define LOG_INCONSISTENT ((const void *)0x0074E9ACU)
#define TRACE_INCONSISTENT ((const void *)0x0070F4E4U)
#define LOG_SIDE ((const void *)0x0074E9D4U)
#define TRACE_SIDE ((const void *)0x00718EC8U)

unsigned int open_cfw_classify_lens_samples(
    const unsigned int samples[5]
);
unsigned int open_cfw_gpio_state_read(
    unsigned int gpio_number,
    unsigned int read_type,
    unsigned int *read_state
);
unsigned int open_cfw_gpio_pinconfig(
    unsigned int gpio_number,
    unsigned int configuration
);

/*
 * Stock ABI: return 1 for the right temple or 2 for the left temple in r0.
 * The original function is an eight-byte load-byte-return accessor.
 */
__attribute__((used, noinline))
unsigned int open_cfw_lens_side(void)
{
    return LENS_SIDE_STATE;
}

/*
 * Complete source replacement for stock 0x0045A578...0x0045A6CF.
 * Preserve the five hardware reads, four 5 ms gaps, diagnostic gates, return
 * values, and the sole publication writes to LENS_SIDE_STATE.
 */
__attribute__((used, noinline))
unsigned int open_cfw_initialize_lens_side(void)
{
    unsigned int samples[5];
    unsigned int index;
    unsigned int flags;
    unsigned int side;

    (void)open_cfw_gpio_pinconfig(0x9CU, LENS_GPIO_CONFIGURATION);
    for (index = 0; index < 5; ++index) {
        unsigned int sample;
        int result = open_cfw_gpio_state_read(0x9CU, 0, &sample);

        if (result != 0) {
            flags = STOCK_LOG_FLAGS();
            if (flags & 2U) {
                STOCK_LOG_RECORD(
                    1U,
                    LOG_MODULE,
                    LOG_FILE,
                    LOG_TAG,
                    0x7FU,
                    LOG_READ_ERROR,
                    index
                );
            }
            flags = STOCK_LOG_FLAGS();
            if ((flags & 1U) || (STOCK_LOG_FLAGS() & 4U)) {
                STOCK_TRACE_RECORD(
                    0x04400000U,
                    TRACE_READ_ERROR,
                    TRACE_READ_ERROR,
                    index
                );
            }
            return 3;
        }

        samples[index] = sample;
        if (index < 4) {
            STOCK_DELAY_MS(5);
        }
    }

    side = open_cfw_classify_lens_samples(samples);
    if (side == 3U) {
        flags = STOCK_LOG_FLAGS();
        if (flags & 2U) {
            STOCK_LOG_RECORD(
                2U,
                LOG_MODULE,
                LOG_FILE,
                LOG_TAG,
                0x91U,
                LOG_INCONSISTENT
            );
        }
        flags = STOCK_LOG_FLAGS();
        if ((flags & 1U) || (STOCK_LOG_FLAGS() & 4U)) {
            STOCK_TRACE_RECORD(
                0x08000000U,
                TRACE_INCONSISTENT,
                TRACE_INCONSISTENT
            );
        }
        return 3;
    }

    flags = STOCK_LOG_FLAGS();
    if (flags & 2U) {
        STOCK_LOG_RECORD(
            4U,
            LOG_MODULE,
            LOG_FILE,
            LOG_TAG,
            0x98U,
            LOG_SIDE,
            samples[0]
        );
    }
    flags = STOCK_LOG_FLAGS();
    if ((flags & 1U) || (STOCK_LOG_FLAGS() & 4U)) {
        STOCK_TRACE_RECORD(
            0x10400000U,
            TRACE_SIDE,
            TRACE_SIDE,
            samples[0]
        );
    }

    LENS_SIDE_STATE = (unsigned char)side;
    return side;
}
