/* Dashboard stock chart rendering and page-state hand-off, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\protocols\dashboard_service\dashboard_data_process.c.
 * Native 0x4ff214..0x4ff277, 0x4ff280..0x4ff2b3, 0x4ff2b8..0x4ff309,
 * 0x4ff31c..0x4ff48b, 0x4ff4c0..0x4ff7d7, 0x4ff7dc..0x4ff84f;
 * literal pools 0x4ff278, 0x4ff2b4, 0x4ff30c, 0x4ff48c..0x4ff4bf, 0x4ff850..0x4ff8d3.
 *
 * Each of the nine stock tiles owns a 1-bpp-as-bytes 132x62 chart bitmap
 * (0x1ff8 bytes, one byte per pixel, 0xff = lit). The chart is drawn with a
 * dashed reference line (previous close) and a connected price polyline, then
 * cleaned out of the D-cache for the display DMA.
 *
 * Hard-float ABI: needs profile g2-apollo-main-3. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define VFP __attribute__((pcs("aapcs-vfp")))

#define STOCK_CHART_COUNT 9u
#define STOCK_BMP_W 132u               /* 0x84 */
#define STOCK_BMP_ROWS 62              /* 0x3e, rows 0..61 */
#define STOCK_ROW_MAX 61               /* 0x3d */
#define STOCK_BMP_SIZE 0x1ff8u         /* 132 * 62 */
#define STOCK_POINTS_MAX 185u          /* validate rejects >= 186 */

/* Message handed to dashboard_send_to_app_serialize 0x4ff09c (same layout as
 * ui/a-15-dashboard/dashboard.c). data_type 3 = page state. */
typedef struct {
    uint32_t package_id;     /* +0x00 */
    uint8_t flag;            /* +0x04 */
    uint8_t data_type;       /* +0x05 */
    uint8_t reserved_06[2];
    uint32_t payload[18];    /* +0x08 */
} g2_dashboard_app_msg_t;
_Static_assert(sizeof(g2_dashboard_app_msg_t) == 0x50u, "dashboard app message");

/* am_hal_cachectrl_range_t */
typedef struct {
    void *start;   /* +0x0 */
    uint32_t size; /* +0x4 */
} g2_cache_range_t;

extern uint8_t g2_stock_bmp_0[STOCK_BMP_SIZE]; /* RAM 0x200bac20 */
extern uint8_t g2_stock_bmp_1[STOCK_BMP_SIZE]; /* RAM 0x200bcc18 */
extern uint8_t g2_stock_bmp_2[STOCK_BMP_SIZE]; /* RAM 0x200bec10 */
extern uint8_t g2_stock_bmp_3[STOCK_BMP_SIZE]; /* RAM 0x200c0c08 */
extern uint8_t g2_stock_bmp_4[STOCK_BMP_SIZE]; /* RAM 0x200c2c00 */
extern uint8_t g2_stock_bmp_5[STOCK_BMP_SIZE]; /* RAM 0x200c4bf8 */
extern uint8_t g2_stock_bmp_6[STOCK_BMP_SIZE]; /* RAM 0x200c6bf0 */
extern uint8_t g2_stock_bmp_7[STOCK_BMP_SIZE]; /* RAM 0x200c8be8 */
extern uint8_t g2_stock_bmp_8[STOCK_BMP_SIZE]; /* RAM 0x200cabe0 */
extern float g2_stock_chart_low[STOCK_CHART_COUNT];   /* RAM 0x20073828, price at row 0 */
extern float g2_stock_chart_scale[STOCK_CHART_COUNT]; /* RAM 0x2007384c, rows per price unit */

extern uint32_t osKernelGetTickCount(void); /* 0x4490cc */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *aeabi_memcpy4_439c04(void *dst, const void *src, uint32_t len);
extern void audio_uart_lv_memzero_48949c(void *dst, uint32_t len);
extern void audio_ble_privacy_cache_maintenance(const g2_cache_range_t *range, uint8_t clean); /* 0x475014 */
extern int32_t dashboard_send_to_app_serialize_4ff09c(const g2_dashboard_app_msg_t *msg);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

#define LOG_E(level, fn, line, ...)                                                          \
    do {                                                                                     \
        if (audio_log_flags() & 2u)                                                          \
            audio_log_extended((level), module_tag, source_file, (fn), (line), __VA_ARGS__); \
    } while (0)
#define LOG_C(code, ...)                                                \
    do {                                                                \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))       \
            (void)compress_log_output((code), __VA_ARGS__);             \
    } while (0)

static const char module_tag[] = "dashboard_data_process"; /* ROM 0x776424 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\dashboard_service\\dashboard_data_process.c"; /* ROM 0x6da4e4 */
static const char validate_fn[] = "validate_stock_data_points"; /* ROM 0x76aa2c */
static const char draw_fn[] = "draw_stock_bmp_by_index";       /* ROM 0x776454 */
static const char send_fn[] = "dashboard_send_page_state_to_app"; /* ROM 0x7532c4 */

static const char y_null[] = "stock y_coords is NULL"; /* ROM 0x77643c */
static const char y_null_short[] = "[dashboard_data_process]stock y_coords is NULL"; /* ROM 0x732bf4 */
static const char total_zero[] = "validate stock point_total is 0"; /* ROM 0x75f090 */
static const char total_zero_short[] = "[dashboard_data_process]validate stock point_total is 0"; /* ROM 0x71d730 */
static const char total_big[] = "validate stock point_total (%d) exceeds maximum (185)"; /* ROM 0x71d768 */
static const char total_big_short[] =
    "[dashboard_data_process]validate stock point_total (%d) exceeds maximum (185)"; /* ROM 0x6ec988 */
static const char range_bad[] = "validate stock Invalid price range: high=%f, low=%f"; /* ROM 0x728518 */
static const char range_bad_short[] =
    "[dashboard_data_process]validate stock Invalid price range: high=%f, low=%f"; /* ROM 0x6f2b00 */
static const char index_bad[] = "draw stock bmp Invalid stock_index = %d"; /* ROM 0x748d54 */
static const char index_bad_short[] = "[dashboard_data_process]draw stock bmp Invalid stock_index = %d"; /* ROM 0x70a7e4 */
static const char points_bad[] = "draw stock bmp Invalid stock data points for stock %d"; /* ROM 0x71d7a0 */
static const char points_bad_short[] =
    "[dashboard_data_process]draw stock bmp Invalid stock data points for stock %d"; /* ROM 0x6ec9d8 */
static const char no_points[] = "draw stock bmp No data points to draw"; /* ROM 0x748d7c */
static const char no_points_short[] = "[dashboard_data_process]draw stock bmp No data points to draw"; /* ROM 0x70a824 */
static const char state_null[] = "dashboard send to app page_state is NULL"; /* ROM 0x73d848 */
static const char state_null_short[] =
    "[dashboard_data_process]dashboard send to app page_state is NULL"; /* ROM 0x701aec */

/* Indices >= 9 fall back to tile 0's bitmap. */
uint8_t *stock_bmp_buffer_by_index_4ff214(uint32_t index)
{
    switch (index) {
    case 0u: return g2_stock_bmp_0;
    case 1u: return g2_stock_bmp_1;
    case 2u: return g2_stock_bmp_2;
    case 3u: return g2_stock_bmp_3;
    case 4u: return g2_stock_bmp_4;
    case 5u: return g2_stock_bmp_5;
    case 6u: return g2_stock_bmp_6;
    case 7u: return g2_stock_bmp_7;
    case 8u: return g2_stock_bmp_8;
    default: return g2_stock_bmp_0;
    }
}

/* Price to chart row, clamped to 0..61 (NaN converts like an in-range value). */
VFP uint8_t stock_price_to_row_4ff280(float price, float low, float scale)
{
    float v = (price - low) * scale;

    if (v < 0.0f)
        return 0u;
    if (v >= 62.0f)
        return (uint8_t)STOCK_ROW_MAX;
    return (uint8_t)(int32_t)v;
}

/* Nearest-sample resampling of count points onto width columns. */
VFP float stock_sample_price_4ff2b8(int32_t column, const float *points, uint32_t count, int32_t width)
{
    uint32_t i;

    if (count == 0u || points == NULL)
        return 0.0f;
    if (count == 1u)
        return points[0];
    i = (uint32_t)(int32_t)(((float)column * (float)count) / (float)width);
    if (i >= count)
        i = count - 1u;
    return points[i];
}

VFP bool validate_stock_data_points_4ff31c(const float *y_coords, uint32_t point_total, float high, float low)
{
    uint32_t i;

    if (y_coords == NULL) {
        LOG_E(1u, validate_fn, 0x65cu, y_null);
        LOG_C(0x04000000u, y_null_short, y_null_short);
        return false;
    }
    if (point_total == 0u) {
        LOG_E(2u, validate_fn, 0x661u, total_zero);
        LOG_C(0x08000000u, total_zero_short, total_zero_short);
        return false;
    }
    if (point_total >= STOCK_POINTS_MAX + 1u) {
        LOG_E(1u, validate_fn, 0x666u, total_big, point_total);
        LOG_C(0x04400000u, total_big_short, total_big_short, point_total);
        return false;
    }
    if (high < low) {
        LOG_E(1u, validate_fn, 0x66bu, range_bad, (double)high, (double)low);
        LOG_C(0x04800000u, range_bad_short, range_bad_short, (double)high, (double)low);
        return false;
    }
    /* Stock keeps an empty per-point loop (its body was compiled out). */
    for (i = 0u; i < point_total; i++) {
    }
    return true;
}

static void stock_plot(uint8_t *bmp, uint32_t offset)
{
    if (offset < STOCK_BMP_SIZE)
        bmp[offset] = 0xffu;
}

/* Stock draw_stock_bmp_by_index. reference is the previous close; the y range
 * is widened to include it. Returns 1 when the bitmap was drawn. */
VFP uint8_t stock_chart_render_4ff4c0(uint32_t index, const float *points, uint32_t count, float high,
                                      float low, float reference)
{
    uint8_t *bmp;
    float base;
    float scale;
    uint8_t row;
    uint8_t prev;
    uint32_t width;
    int32_t x;
    int32_t j;
    bool first;
    g2_cache_range_t range;

    if (high <= 0.0f || low < 0.0f || high < low)
        return 0u;
    if (index >= STOCK_CHART_COUNT) {
        LOG_E(1u, draw_fn, 0x690u, index_bad, index);
        LOG_C(0x04400000u, index_bad_short, index_bad_short, index);
        return 0u;
    }
    (void)osKernelGetTickCount();
    bmp = stock_bmp_buffer_by_index_4ff214(index);
    (void)aeabi_memset_43c0e4(bmp, STOCK_BMP_SIZE, 0);
    if (!validate_stock_data_points_4ff31c(points, count, high, low)) {
        LOG_E(1u, draw_fn, 0x69cu, points_bad, index);
        LOG_C(0x04400000u, points_bad_short, points_bad_short, index);
        return 0u;
    }
    if (count == 0u || points == NULL) {
        LOG_E(2u, draw_fn, 0x6a3u, no_points);
        LOG_C(0x08000000u, no_points_short, no_points_short);
        return 0u;
    }

    g2_stock_chart_low[index] = (low < reference) ? low : reference;
    if (high < reference)
        high = reference;
    if (!(low < reference))
        low = reference;
    g2_stock_chart_scale[index] = 62.0f / (high - low);
    base = g2_stock_chart_low[index];
    scale = g2_stock_chart_scale[index];

    /* Dashed reference line: 6 lit pixels, 2 dark. */
    row = (uint8_t)(int32_t)((reference - base) * scale);
    if (row >= (uint8_t)STOCK_BMP_ROWS)
        row = (uint8_t)STOCK_ROW_MAX;
    for (x = 0; x < (int32_t)STOCK_BMP_W; x++) {
        if (x % 8 != 6 && x % 8 != 7)
            bmp[(STOCK_ROW_MAX - (int32_t)row) * (int32_t)STOCK_BMP_W + x] = 0xffu;
    }

    if (count >= STOCK_POINTS_MAX)
        width = STOCK_BMP_W;
    else if (count < STOCK_BMP_W)
        width = count;
    else
        width = STOCK_BMP_W;

    /* Price polyline; vertical runs join consecutive columns. */
    first = true;
    prev = 0u;
    for (x = 0; x < (int32_t)width; x++) {
        row = stock_price_to_row_4ff280(stock_sample_price_4ff2b8(x, points, count, (int32_t)width), base, scale);
        if (first) {
            stock_plot(bmp, (uint32_t)((STOCK_ROW_MAX - (int32_t)row) * (int32_t)STOCK_BMP_W + x));
            first = false;
        } else if (row < prev) {
            for (j = 0; j <= (int32_t)(uint8_t)(prev - row); j++)
                stock_plot(bmp, (uint32_t)(((STOCK_ROW_MAX - (int32_t)row) - j) * (int32_t)STOCK_BMP_W + x));
        } else if (prev < row) {
            for (j = 0; j <= (int32_t)(uint8_t)(row - prev); j++)
                stock_plot(bmp, (uint32_t)((j + (STOCK_ROW_MAX - (int32_t)row)) * (int32_t)STOCK_BMP_W + x));
        } else {
            stock_plot(bmp, (uint32_t)((STOCK_ROW_MAX - (int32_t)row) * (int32_t)STOCK_BMP_W + x));
        }
        prev = row;
    }

    (void)osKernelGetTickCount();
    range.start = bmp;
    range.size = STOCK_BMP_SIZE;
    audio_ble_privacy_cache_maintenance(&range, 1u);
    return 1u;
}

/* Wraps a 64-byte page-state record (page_state_sync.c) as data_type 3.
 * Returns 1 for a NULL record, otherwise the serializer result. */
int32_t dashboard_send_page_state_to_app_4ff7dc(uint32_t package_id, uint8_t flag, const void *page_state)
{
    g2_dashboard_app_msg_t msg;

    if (page_state == NULL) {
        LOG_E(1u, send_fn, 0x717u, state_null);
        LOG_C(0x04000000u, state_null_short, state_null_short);
        return 1;
    }
    audio_uart_lv_memzero_48949c(&msg, sizeof msg);
    msg.package_id = package_id;
    msg.flag = flag;
    msg.data_type = 3u;
    (void)aeabi_memcpy4_439c04(msg.payload, page_state, 0x40u);
    return dashboard_send_to_app_serialize_4ff09c(&msg);
}
