/*
 * SPDX-License-Identifier: MIT
 *
 * EvenHub common-data callback replacement for the Even Realities G2
 * 2.2.6.10 Apollo510B application. Exact stock boundaries, callback-table
 * evidence, event/subtype behavior, diagnostics, and ABI dependencies are
 * recorded in EVIDENCE.md.
 */

typedef unsigned int (*open_cfw_evenhub_common_forward_fn)(
    const unsigned char *data,
    unsigned int length
);
typedef unsigned int (*open_cfw_evenhub_common_peer_active_fn)(void);
typedef unsigned int (*open_cfw_evenhub_common_peer_registered_fn)(
    unsigned int device
);
typedef void (*open_cfw_evenhub_common_send_status_fn)(
    unsigned int arg0,
    unsigned int arg1,
    unsigned int arg2,
    unsigned int status,
    unsigned int arg4,
    unsigned int arg5
);
typedef unsigned int (*open_cfw_evenhub_common_display_stop_fn)(
    unsigned int device,
    unsigned int arg1,
    unsigned int arg2,
    unsigned int arg3
);

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_EVENHUB_COMMON_VFP_PCS \
    __attribute__((pcs("aapcs-vfp")))
#else
#define OPEN_CFW_EVENHUB_COMMON_VFP_PCS
#endif

typedef unsigned int (*open_cfw_evenhub_common_report_imu_fn)(
    float x,
    float y,
    float z
) OPEN_CFW_EVENHUB_COMMON_VFP_PCS;

typedef unsigned int (*open_cfw_evenhub_common_log_flags_fn)(void);
typedef void (*open_cfw_evenhub_common_log_record_fn)(
    unsigned int level,
    const void *module,
    const void *file,
    const void *tag,
    unsigned int line,
    const void *format,
    ...
);
typedef void (*open_cfw_evenhub_common_trace_record_fn)(
    unsigned int mask,
    const void *schema,
    const void *format,
    ...
);

#ifndef OPEN_CFW_EVENHUB_COMMON_FORWARD
#define OPEN_CFW_EVENHUB_COMMON_FORWARD(data, length) \
    (((open_cfw_evenhub_common_forward_fn)0x004DA835U)( \
        (data), \
        (length) \
    ))
#endif

#ifndef OPEN_CFW_EVENHUB_COMMON_PEER_ACTIVE
#define OPEN_CFW_EVENHUB_COMMON_PEER_ACTIVE() \
    (((open_cfw_evenhub_common_peer_active_fn)0x00443485U)())
#endif

#ifndef OPEN_CFW_EVENHUB_COMMON_PEER_REGISTERED
#define OPEN_CFW_EVENHUB_COMMON_PEER_REGISTERED(device) \
    (((open_cfw_evenhub_common_peer_registered_fn)0x004434D1U)(device))
#endif

#ifndef OPEN_CFW_EVENHUB_COMMON_SEND_STATUS
#define OPEN_CFW_EVENHUB_COMMON_SEND_STATUS(a0, a1, a2, status, a4, a5) \
    (((open_cfw_evenhub_common_send_status_fn)0x004DA16BU)( \
        (a0), \
        (a1), \
        (a2), \
        (status), \
        (a4), \
        (a5) \
    ))
#endif

#ifndef OPEN_CFW_EVENHUB_COMMON_REQUEST_DISPLAY_STOP
#define OPEN_CFW_EVENHUB_COMMON_REQUEST_DISPLAY_STOP(device, a1, a2, a3) \
    (((open_cfw_evenhub_common_display_stop_fn)0x00464C37U)( \
        (device), \
        (a1), \
        (a2), \
        (a3) \
    ))
#endif

#ifndef OPEN_CFW_EVENHUB_COMMON_REPORT_IMU
#define OPEN_CFW_EVENHUB_COMMON_REPORT_IMU(x, y, z) \
    (((open_cfw_evenhub_common_report_imu_fn)0x004D9F6FU)((x), (y), (z)))
#endif

#ifndef OPEN_CFW_EVENHUB_COMMON_LOG_FLAGS
#define OPEN_CFW_EVENHUB_COMMON_LOG_FLAGS \
    ((open_cfw_evenhub_common_log_flags_fn)0x0043D0CFU)
#endif

#ifndef OPEN_CFW_EVENHUB_COMMON_LOG_RECORD
#define OPEN_CFW_EVENHUB_COMMON_LOG_RECORD \
    ((open_cfw_evenhub_common_log_record_fn)0x0043D575U)
#endif

#ifndef OPEN_CFW_EVENHUB_COMMON_TRACE_RECORD
#define OPEN_CFW_EVENHUB_COMMON_TRACE_RECORD \
    ((open_cfw_evenhub_common_trace_record_fn)0x0043CE9FU)
#endif

#define OPEN_CFW_EVENHUB_COMMON_DEVICE 0xE0U
#define OPEN_CFW_EVENHUB_COMMON_EVENT 5U
#define OPEN_CFW_EVENHUB_COMMON_ABNORMAL_EXIT 0U
#define OPEN_CFW_EVENHUB_COMMON_IMU_REPORT 1U
#define OPEN_CFW_EVENHUB_COMMON_ERROR 0xFFFFFFFFU

#define OPEN_CFW_EVENHUB_COMMON_LOG_MODULE ((const void *)0x00785E70U)
#define OPEN_CFW_EVENHUB_COMMON_LOG_FILE ((const void *)0x00702988U)
#define OPEN_CFW_EVENHUB_COMMON_LOG_TAG ((const void *)0x0076B848U)

#define OPEN_CFW_EVENHUB_COMMON_EVENT_FORMAT ((const void *)0x0073ED40U)
#define OPEN_CFW_EVENHUB_COMMON_EVENT_TRACE ((const void *)0x007150ACU)
#define OPEN_CFW_EVENHUB_COMMON_NULL_ERROR ((const void *)0x006DD2F4U)
#define OPEN_CFW_EVENHUB_COMMON_NULL_TRACE ((const void *)0x006CA6A4U)
#define OPEN_CFW_EVENHUB_COMMON_ABNORMAL_LOG ((const void *)0x006D899CU)
#define OPEN_CFW_EVENHUB_COMMON_ABNORMAL_TRACE ((const void *)0x006A01CCU)
#define OPEN_CFW_EVENHUB_COMMON_IMU_LOG ((const void *)0x006DD354U)
#define OPEN_CFW_EVENHUB_COMMON_IMU_TRACE ((const void *)0x006D6FD0U)
#define OPEN_CFW_EVENHUB_COMMON_SHORT_LOG ((const void *)0x006A05C4U)
#define OPEN_CFW_EVENHUB_COMMON_SHORT_TRACE ((const void *)0x006D4FC4U)
#define OPEN_CFW_EVENHUB_COMMON_FLOAT_LOG ((const void *)0x007775F4U)
#define OPEN_CFW_EVENHUB_COMMON_FLOAT_TRACE ((const void *)0x0074A014U)

static inline __attribute__((always_inline))
unsigned int open_cfw_evenhub_common_trace_enabled(void)
{
    unsigned int flags = OPEN_CFW_EVENHUB_COMMON_LOG_FLAGS();

    if (flags & 1U) {
        return 1U;
    }
    return (OPEN_CFW_EVENHUB_COMMON_LOG_FLAGS() & 4U) != 0U;
}

static inline __attribute__((always_inline))
void open_cfw_evenhub_common_fixed_diagnostic(
    unsigned int level,
    unsigned int line,
    const void *message,
    unsigned int trace_mask,
    const void *trace_schema
)
{
    if (OPEN_CFW_EVENHUB_COMMON_LOG_FLAGS() & 2U) {
        OPEN_CFW_EVENHUB_COMMON_LOG_RECORD(
            level,
            OPEN_CFW_EVENHUB_COMMON_LOG_MODULE,
            OPEN_CFW_EVENHUB_COMMON_LOG_FILE,
            OPEN_CFW_EVENHUB_COMMON_LOG_TAG,
            line,
            message
        );
    }
    if (open_cfw_evenhub_common_trace_enabled()) {
        OPEN_CFW_EVENHUB_COMMON_TRACE_RECORD(
            trace_mask,
            trace_schema,
            trace_schema
        );
    }
}

static inline __attribute__((always_inline))
unsigned int open_cfw_evenhub_common_load_u32(
    const unsigned char *source
)
{
    return
        (unsigned int)source[0] |
        ((unsigned int)source[1] << 8) |
        ((unsigned int)source[2] << 16) |
        ((unsigned int)source[3] << 24);
}

static inline __attribute__((always_inline))
float open_cfw_evenhub_common_float_from_bits(unsigned int bits)
{
    union {
        unsigned int bits;
        float value;
    } decoded;

    decoded.bits = bits;
    return decoded.value;
}

/*
 * The stock diagnostic promotes each float32 to a variadic double. Building
 * the IEEE-754 double words directly avoids pulling the freestanding
 * __aeabi_f2d runtime into the append-only overlay.
 */
static inline __attribute__((always_inline))
double open_cfw_evenhub_common_double_from_float_bits(unsigned int bits)
{
    union {
        struct {
            unsigned int low;
            unsigned int high;
        } words;
        double value;
    } decoded;
    unsigned int sign = bits & 0x80000000U;
    unsigned int exponent = (bits >> 23) & 0xFFU;
    unsigned int fraction = bits & 0x007FFFFFU;

    decoded.words.low = 0U;
    decoded.words.high = sign;
    if (exponent == 0U) {
        unsigned int shift = 0U;

        if (fraction == 0U) {
            return decoded.value;
        }
        while ((fraction & 0x00800000U) == 0U) {
            fraction <<= 1;
            ++shift;
        }
        fraction &= 0x007FFFFFU;
        decoded.words.high |= (897U - shift) << 20;
    } else if (exponent == 0xFFU) {
        decoded.words.high |= 0x7FF00000U;
    } else {
        decoded.words.high |= (exponent + 896U) << 20;
    }
    decoded.words.high |= fraction >> 3;
    decoded.words.low = fraction << 29;
    return decoded.value;
}

/*
 * ABI-compatible source replacement for stock 0x004E1192...0x004E1405.
 *
 * Event zero is forwarded unchanged. Event five carries private EvenHub
 * control data: subtype zero reports abnormal exit and stops display device
 * 0xE0, while subtype one decodes three little-endian IEEE-754 float32
 * samples and reports them with the stock hard-float AAPCS convention.
 *
 * The callback's registration site treats its return as opaque. Meaningful
 * stock paths are preserved exactly: forwarded and downstream return values,
 * 0xFFFFFFFF validation errors, and the untouched subtype for unknown private
 * records. Other event types have no functional side effects and return zero.
 */
__attribute__((used, noinline))
unsigned int open_cfw_evenhub_common_data_handler(
    unsigned int event_type,
    const unsigned char *data,
    unsigned int length,
    unsigned int unused
)
{
    unsigned int subtype;
    unsigned int x_bits;
    unsigned int y_bits;
    unsigned int z_bits;
    float x;
    float y;
    float z;

    (void)unused;

    if (OPEN_CFW_EVENHUB_COMMON_LOG_FLAGS() & 2U) {
        OPEN_CFW_EVENHUB_COMMON_LOG_RECORD(
            4U,
            OPEN_CFW_EVENHUB_COMMON_LOG_MODULE,
            OPEN_CFW_EVENHUB_COMMON_LOG_FILE,
            OPEN_CFW_EVENHUB_COMMON_LOG_TAG,
            0xD9U,
            OPEN_CFW_EVENHUB_COMMON_EVENT_FORMAT,
            event_type
        );
    }
    if (open_cfw_evenhub_common_trace_enabled()) {
        OPEN_CFW_EVENHUB_COMMON_TRACE_RECORD(
            0x10400000U,
            OPEN_CFW_EVENHUB_COMMON_EVENT_TRACE,
            OPEN_CFW_EVENHUB_COMMON_EVENT_TRACE,
            event_type
        );
    }

    if (event_type == 0U) {
        return OPEN_CFW_EVENHUB_COMMON_FORWARD(data, length);
    }
    if (event_type != OPEN_CFW_EVENHUB_COMMON_EVENT) {
        return 0U;
    }

    if (
        (data == (const unsigned char *)0 || length == 0U) &&
        (
            OPEN_CFW_EVENHUB_COMMON_PEER_ACTIVE() == 0U ||
            OPEN_CFW_EVENHUB_COMMON_PEER_REGISTERED(
                OPEN_CFW_EVENHUB_COMMON_DEVICE
            ) == 0U
        )
    ) {
        open_cfw_evenhub_common_fixed_diagnostic(
            1U,
            0xDFU,
            OPEN_CFW_EVENHUB_COMMON_NULL_ERROR,
            0x04000000U,
            OPEN_CFW_EVENHUB_COMMON_NULL_TRACE
        );
        return OPEN_CFW_EVENHUB_COMMON_ERROR;
    }

    subtype = data[0];
    if (subtype == OPEN_CFW_EVENHUB_COMMON_ABNORMAL_EXIT) {
        open_cfw_evenhub_common_fixed_diagnostic(
            1U,
            0xE5U,
            OPEN_CFW_EVENHUB_COMMON_ABNORMAL_LOG,
            0x04000000U,
            OPEN_CFW_EVENHUB_COMMON_ABNORMAL_TRACE
        );
        OPEN_CFW_EVENHUB_COMMON_SEND_STATUS(0U, 0U, 0U, 6U, 0U, 0U);
        return OPEN_CFW_EVENHUB_COMMON_REQUEST_DISPLAY_STOP(
            OPEN_CFW_EVENHUB_COMMON_DEVICE,
            0U,
            0U,
            0U
        );
    }
    if (subtype != OPEN_CFW_EVENHUB_COMMON_IMU_REPORT) {
        return subtype;
    }

    open_cfw_evenhub_common_fixed_diagnostic(
        4U,
        0xEAU,
        OPEN_CFW_EVENHUB_COMMON_IMU_LOG,
        0x10000000U,
        OPEN_CFW_EVENHUB_COMMON_IMU_TRACE
    );
    if (length < 13U) {
        open_cfw_evenhub_common_fixed_diagnostic(
            1U,
            0xECU,
            OPEN_CFW_EVENHUB_COMMON_SHORT_LOG,
            0x04000000U,
            OPEN_CFW_EVENHUB_COMMON_SHORT_TRACE
        );
        return OPEN_CFW_EVENHUB_COMMON_ERROR;
    }

    x_bits = open_cfw_evenhub_common_load_u32(data + 1);
    y_bits = open_cfw_evenhub_common_load_u32(data + 5);
    z_bits = open_cfw_evenhub_common_load_u32(data + 9);
    x = open_cfw_evenhub_common_float_from_bits(x_bits);
    y = open_cfw_evenhub_common_float_from_bits(y_bits);
    z = open_cfw_evenhub_common_float_from_bits(z_bits);

    if (OPEN_CFW_EVENHUB_COMMON_LOG_FLAGS() & 2U) {
        OPEN_CFW_EVENHUB_COMMON_LOG_RECORD(
            4U,
            OPEN_CFW_EVENHUB_COMMON_LOG_MODULE,
            OPEN_CFW_EVENHUB_COMMON_LOG_FILE,
            OPEN_CFW_EVENHUB_COMMON_LOG_TAG,
            0xF3U,
            OPEN_CFW_EVENHUB_COMMON_FLOAT_LOG,
            open_cfw_evenhub_common_double_from_float_bits(x_bits),
            open_cfw_evenhub_common_double_from_float_bits(y_bits),
            open_cfw_evenhub_common_double_from_float_bits(z_bits)
        );
    }
    if (open_cfw_evenhub_common_trace_enabled()) {
        OPEN_CFW_EVENHUB_COMMON_TRACE_RECORD(
            0x10C00000U,
            OPEN_CFW_EVENHUB_COMMON_FLOAT_TRACE,
            OPEN_CFW_EVENHUB_COMMON_FLOAT_TRACE
        );
    }

    return OPEN_CFW_EVENHUB_COMMON_REPORT_IMU(x, y, z);
}
