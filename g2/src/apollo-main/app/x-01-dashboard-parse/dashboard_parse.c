/* Stock D:\01_workspace\s200_ap510b_iar_git\platform\protocols\dashboard_service\dashboard_data_process.c
 * (log tag "dashboard_data_process"), parsed-buffer side of the dashboard service.
 * Native 0x4FD93C..0x4FDA23, 0x4FDA24..0x4FDAD3, 0x4FDAD4..0x4FDD6D,
 * 0x4FDF08..0x4FDF73, 0x4FDF74..0x4FE0A9 (literal pools shared with the
 * protobuf part, 0x4FE2C4..0x4FE317 and 0x4FEC04). The protobuf side of the
 * same TU is app/a-38-dashboard-data-process/dashboard_data_process.c.
 *
 * Parsed package (caller buffer, 0x14c0 bytes; consumer
 * dashboard_async_update_data 0x49ce14):
 *   +0x0020 weather block (valid u8, 0x80 bytes), mirrored at +0x00a0, +0x0120 icon
 *   +0x0150 legacy news record, +0x0e20/+0x0e24/+0x0e28 news counters
 *   +0x0e30 stock record, +0x1258 stock_total, +0x125c stock_num
 *   +0x1260 schedule record, +0x1478 schedule_total, +0x147c schedule_num
 *   +0x14b0 has weather, +0x14b3 has news, +0x14b4 has stock, +0x14b5 has schedule
 *
 * The stock record copies two doubles (+0x100, +0x128) through d0 in stock; they
 * are copied as 64-bit words here, so no float code is needed. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define PARSED_SIZE         0x14c0u
#define PARSED_WEATHER      0x0020u
#define PARSED_WEATHER_COPY 0x00a0u
#define PARSED_WEATHER_ICON 0x0120u
#define PARSED_NEWS         0x0150u
#define PARSED_NEWS_TOTAL   0x0e20u
#define PARSED_NEWS_INDEX   0x0e24u
#define PARSED_NEWS_0E28    0x0e28u
#define PARSED_STOCK        0x0e30u
#define PARSED_STOCK_TOTAL  0x1258u
#define PARSED_STOCK_NUM    0x125cu
#define PARSED_SCHEDULE     0x1260u
#define PARSED_SCHED_TOTAL  0x1478u
#define PARSED_SCHED_NUM    0x147cu
#define PARSED_HAS_WEATHER  0x14b0u
#define PARSED_HAS_NEWS     0x14b3u
#define PARSED_HAS_STOCK    0x14b4u
#define PARSED_HAS_SCHEDULE 0x14b5u

#define STOCK_POINTS_MAX 185u
#define WAIT_FOREVER     0xffffffffu

#define P8(b, o)  (*(uint8_t *)((uint8_t *)(b) + (o)))
#define P16(b, o) (*(uint16_t *)(void *)((uint8_t *)(b) + (o)))
#define P32(b, o) (*(uint32_t *)(void *)((uint8_t *)(b) + (o)))
#define P64(b, o) (*(uint64_t *)(void *)((uint8_t *)(b) + (o)))
#define C8(b, o)  (*(const uint8_t *)((const uint8_t *)(b) + (o)))
#define C16(b, o) (*(const uint16_t *)(const void *)((const uint8_t *)(b) + (o)))
#define C32(b, o) (*(const uint32_t *)(const void *)((const uint8_t *)(b) + (o)))
#define C64(b, o) (*(const uint64_t *)(const void *)((const uint8_t *)(b) + (o)))

/* One news session (0x1ca8 bytes), five in g2_news_staging_203024a4
 * (same layout as app/a-38-dashboard-data-process). */
typedef struct {
    uint8_t valid;            /* +0x0000 */
    uint8_t pad_01[3];
    uint32_t session_id;      /* +0x0004 */
    uint32_t field_08;        /* +0x0008 */
    uint32_t news_index;      /* +0x000c */
    uint32_t news_id;         /* +0x0010 */
    char text_14[0x80];       /* +0x0014 source */
    char text_94[0x80];       /* +0x0094 title */
    char body[0x1b8a];        /* +0x0114 */
    uint8_t pad_1c9e[2];
    uint32_t stamp[2];        /* +0x1ca0 u64 publish time (ms) */
} g2_news_session_t;
_Static_assert(sizeof(g2_news_session_t) == 0x1ca8u, "news session record");

/* One display news record (0x1c98 bytes), five in g2_dashboard_news_cache_20132f74. */
typedef struct {
    uint8_t valid;            /* +0x0000 */
    char source[0x80];        /* +0x0001 */
    char title[0x80];         /* +0x0081 */
    char body[0x1b8a];        /* +0x0101 */
    uint8_t pad_1c8b;
    uint32_t news_id;         /* +0x1c8c */
    uint32_t stamp[2];        /* +0x1c90 */
} g2_news_disp_record_t;
_Static_assert(offsetof(g2_news_disp_record_t, news_id) == 0x1c8cu, "news id");
_Static_assert(sizeof(g2_news_disp_record_t) == 0x1c98u, "news display record");

#define NEWS_SLOTS 5u

/* RAM state (the pointers are file-scope statics in stock, kept in RAM). */
extern const uint8_t *g2_dashboard_weather_src_200743dc;   /* RAM 0x200743dc */
extern uint32_t g2_dashboard_news_index_base_200743e0;     /* RAM 0x200743e0 */
extern const uint8_t *g2_dashboard_news_src_200743e4;      /* RAM 0x200743e4 */
extern const uint8_t *g2_dashboard_news_item_src_200743e8; /* RAM 0x200743e8 */
extern uint8_t *g2_dashboard_news_dst_200743ec;            /* RAM 0x200743ec */
extern const uint8_t *g2_dashboard_stock_src_200743f0;     /* RAM 0x200743f0 */
extern const uint8_t *g2_dashboard_stock_item_src_200743f4; /* RAM 0x200743f4 */
extern uint8_t *g2_dashboard_stock_dst_200743f8;           /* RAM 0x200743f8 */
extern const uint8_t *g2_dashboard_sched_src_200743fc;     /* RAM 0x200743fc */
extern const uint8_t *g2_dashboard_sched_item_src_20074400; /* RAM 0x20074400 */
extern uint8_t *g2_dashboard_sched_dst_20074404;           /* RAM 0x20074404 */
extern uint32_t g2_dashboard_news_index_200005d8;          /* RAM 0x200005d8 */
extern uint8_t g2_news_staging_203024a4[0x8f48];           /* RAM 0x203024a4 */
extern uint8_t g2_dashboard_news_cache_20132f74[0x8ef8];   /* RAM 0x20132f74 */
extern void *g2_dashboard_mutex_200743a8;                  /* RAM 0x200743a8 osMutexId */

/* Runtime. */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *audio_uart_display_area_copy_439c04(void *dst, const void *src, uint32_t len); /* memcpy */
extern void *audio_settings_copy_text(void *dst, const void *src, uint32_t len); /* strncpy 0x44b5a0 */
extern int32_t osMutexAcquire(void *mutex, uint32_t timeout);   /* 0x4497b6 */
extern int32_t osMutexRelease(void *mutex);                     /* 0x44981c */

/* Logging. */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

void dashboard_parsed_data_reset_4fd93c(uint8_t *parsed);
uint32_t dashboard_parse_weather_4fda24(const uint8_t *weather, uint8_t *parsed);
uint32_t dashboard_parse_widget_data_4fdad4(const uint8_t *widget, uint8_t *parsed);
void clear_news_cache_data_to_disp_buffer_4fdf08(void);
uint32_t load_news_cache_data_to_disp_buffer_4fdf74(uint8_t *news_widget_data);

static const char tag[] = "dashboard_data_process"; /* ROM 0x776424 */
static const char src[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\dashboard_service\\dashboard_data_process.c"; /* ROM 0x6da4e4 */
static const char fn_clear[] = "clear_news_cache_data_to_disp_buffer"; /* ROM 0x748cdc */
static const char m_clear[] = "clear news cache data to disp buffer"; /* ROM 0x748d04 */
static const char t_clear[] = "[dashboard_data_process]clear news cache data to disp buffer"; /* ROM 0x70a724 */
static const char fn_load[] = "load_news_cache_data_to_disp_buffer"; /* ROM 0x753234 */
static const char m_load_null[] = "news_widget_data is NULL"; /* ROM 0x76a9f4 */
static const char t_load_null[] = "[dashboard_data_process]news_widget_data is NULL"; /* ROM 0x728414 */

/* Stock log macro expansion (level in bits 26..28, argument count in 22..25). */
#define DP_LOG(lvl, fn, line, nargs, m, t, ...)                                              \
    do {                                                                                     \
        if ((audio_log_flags() & 2u) != 0u)                                                  \
            audio_log_extended((lvl), tag, src, (fn), (line), (m), ##__VA_ARGS__);           \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                \
            (void)compress_log_output(((uint32_t)(lvl) << 26) | ((uint32_t)(nargs) << 22),   \
                                      (t), (t), ##__VA_ARGS__);                              \
    } while (0)

/* Clears the whole buffer, then repeats the generated per-field zeroing. */
void dashboard_parsed_data_reset_4fd93c(uint8_t *parsed)
{
    if (parsed == NULL)
        return;
    (void)aeabi_memset_43c0e4(parsed, PARSED_SIZE, 0);
    P32(parsed, 0x1480u) = 0u;
    P32(parsed, 0x1484u) = 0u;
    P32(parsed, 0x1494u) = 0u;
    P8(parsed, PARSED_WEATHER) = 0u;
    P32(parsed, 0x24u) = 0u;
    P16(parsed, 0x28u) = 0u;
    P16(parsed, 0x2au) = 0u;
    P64(parsed, 0x30u) = 0u;
    (void)aeabi_memset_43c0e4(parsed + 0xa0u, 0x88u, 0);
    (void)aeabi_memset_43c0e4(parsed + 0x128u, 0x10u, 0);
    (void)aeabi_memset_43c0e4(parsed + 0x138u, 0x18u, 0);
    P32(parsed, PARSED_NEWS_TOTAL) = 0u;
    P32(parsed, PARSED_NEWS_INDEX) = 0u;
    P32(parsed, PARSED_STOCK_TOTAL) = 0u;
    P32(parsed, PARSED_STOCK_NUM) = 0u;
    P32(parsed, PARSED_SCHED_TOTAL) = 0u;
    P32(parsed, PARSED_SCHED_NUM) = 0u;
    for (uint32_t o = PARSED_HAS_WEATHER; o <= 0x14b8u; o++)
        P8(parsed, o) = 0u;
}

/* weather: pb submessage {has u8 +0, payload +8}. Returns 0 only for NULL args. */
uint32_t dashboard_parse_weather_4fda24(const uint8_t *weather, uint8_t *parsed)
{
    const uint8_t *w;

    if (weather == NULL || parsed == NULL)
        return 0u;
    if (weather[0] == 0u)
        return 1u;
    g2_dashboard_weather_src_200743dc = weather + 8;
    P8(parsed, 0x20u) = 1u;
    w = g2_dashboard_weather_src_200743dc;
    P32(parsed, 0x24u) = C32(w, 0x00u);
    P16(parsed, 0x28u) = C8(w, 0x04u);
    P16(parsed, 0x2au) = C8(w, 0x05u);
    P64(parsed, 0x30u) = C64(w, 0x08u);
    (void)audio_settings_copy_text(parsed + 0x38u, w + 0x10u, 31u);
    P8(parsed, 0x57u) = 0u;
    P32(parsed, 0x58u) = C32(w, 0x30u);
    (void)audio_settings_copy_text(parsed + 0x5cu, w + 0x34u, 31u);
    P8(parsed, 0x7bu) = 0u;
    P32(parsed, 0x7cu) = C32(w, 0x54u);
    (void)audio_settings_copy_text(parsed + 0x80u, w + 0x58u, 31u);
    P8(parsed, 0x9fu) = 0u;
    (void)audio_uart_display_area_copy_439c04(parsed + PARSED_WEATHER_COPY, parsed + PARSED_WEATHER,
                                              0x80u);
    P8(parsed, PARSED_WEATHER_ICON) = C8(w, 0x05u);
    P8(parsed, PARSED_HAS_WEATHER) = 1u;
    return 1u;
}

static void parse_news(const uint8_t *body, uint8_t *parsed)
{
    const uint8_t *n;
    uint32_t next;

    g2_dashboard_news_src_200743e4 = body;
    g2_dashboard_news_item_src_200743e8 = g2_dashboard_news_src_200743e4 + 0x10u;
    n = g2_dashboard_news_src_200743e4;
    P32(parsed, PARSED_NEWS_TOTAL) = C32(n, 0x00u);
    P32(parsed, PARSED_NEWS_INDEX) = C32(n, 0x04u) - g2_dashboard_news_index_base_200743e0;
    P32(parsed, PARSED_NEWS_0E28) = C32(n, 0xcd8u);
    g2_dashboard_news_index_200005d8 = C32(n, 0x04u);
    if (C32(n, 0x04u) == 0u)
        g2_dashboard_news_index_base_200743e0 = 0u;
    /* Last item of a batch: the next batch's indices are relative to this one. */
    next = C32(n, 0x04u) + 1u - g2_dashboard_news_index_base_200743e0;
    if (next == C32(n, 0x00u))
        g2_dashboard_news_index_base_200743e0 = C32(n, 0x00u) + g2_dashboard_news_index_base_200743e0;
    g2_dashboard_news_dst_200743ec = parsed + PARSED_NEWS;
    P32(g2_dashboard_news_dst_200743ec, 0x000u) = C32(g2_dashboard_news_item_src_200743e8, 0x00u);
    P64(g2_dashboard_news_dst_200743ec, 0xcc0u) = C64(g2_dashboard_news_item_src_200743e8, 0x88u);
    P8(g2_dashboard_news_dst_200743ec, 0xcc8u) = 0u;
    P8(parsed, PARSED_HAS_NEWS) = 1u;
}

static void parse_stock(const uint8_t *body, uint8_t *parsed)
{
    int32_t i;

    g2_dashboard_stock_src_200743f0 = body;
    g2_dashboard_stock_item_src_200743f4 = g2_dashboard_stock_src_200743f0 + 0x10u;
    P32(parsed, PARSED_STOCK_TOTAL) = C32(g2_dashboard_stock_src_200743f0, 0x00u);
    P32(parsed, PARSED_STOCK_NUM) = C32(g2_dashboard_stock_src_200743f0, 0x04u);
    g2_dashboard_stock_dst_200743f8 = parsed + PARSED_STOCK;
#define SD g2_dashboard_stock_dst_200743f8
#define SS g2_dashboard_stock_item_src_200743f4
    P64(SD, 0x100u) = C64(SS, 0x80u); /* double */
    P32(SD, 0x108u) = C32(SS, 0x88u);
    P32(SD, 0x10cu) = C32(SS, 0x8cu);
    P32(SD, 0x110u) = C32(SS, 0x110u);
    P32(SD, 0x114u) = C32(SS, 0x114u);
    P32(SD, 0x118u) = C32(SS, 0x118u);
    P64(SD, 0x120u) = C64(SS, 0x120u);
    P64(SD, 0x128u) = C64(SS, 0x128u); /* double */
    P32(SD, 0x130u) = C32(SS, 0x130u);
    P32(SD, 0x134u) = C32(SS, 0x134u);
    P32(SD, 0x138u) = C32(SS, 0x138u);
    P32(SD, 0x13cu) = C32(SS, 0x13cu);
    (void)audio_settings_copy_text(SD, SS, 63u);
    P8(SD, 0x3fu) = 0u;
    (void)audio_settings_copy_text(SD + 0x40u, SS + 0x40u, 63u);
    P8(SD, 0x7fu) = 0u;
    (void)audio_settings_copy_text(SD + 0x80u, SS + 0x90u, 127u);
    P8(SD, 0xffu) = 0u;
    /* chart points: pb repeated {u16 count +0x140, u32[] +0x144} */
    for (i = 0; i < (int32_t)C16(SS, 0x140u) && (uint32_t)i < STOCK_POINTS_MAX; i++)
        P32(SD, 0x140u + 4u * (uint32_t)i) = C32(SS, 0x144u + 4u * (uint32_t)i);
#undef SD
#undef SS
    P8(parsed, PARSED_HAS_STOCK) = 1u;
}

static void parse_schedule(const uint8_t *body, uint8_t *parsed)
{
    g2_dashboard_sched_src_200743fc = body;
    g2_dashboard_sched_item_src_20074400 = g2_dashboard_sched_src_200743fc + 0x0cu;
    P32(parsed, PARSED_SCHED_TOTAL) = C32(g2_dashboard_sched_src_200743fc, 0x00u);
    P32(parsed, PARSED_SCHED_NUM) = C32(g2_dashboard_sched_src_200743fc, 0x04u);
    g2_dashboard_sched_dst_20074404 = parsed + PARSED_SCHEDULE;
#define DD g2_dashboard_sched_dst_20074404
#define DS g2_dashboard_sched_item_src_20074400
    P32(DD, 0x000u) = C32(DS, 0x000u);
    (void)audio_settings_copy_text(DD + 0x004u, DS + 0x004u, 0xafu);
    P8(DD, 0x0b3u) = 0u;
    (void)audio_settings_copy_text(DD + 0x0b4u, DS + 0x0b4u, 0x11au);
    P8(DD, 0x1ceu) = 0u;
    (void)audio_settings_copy_text(DD + 0x1cfu, DS + 0x1cfu, 0x3fu);
    P8(DD, 0x20eu) = 0u;
    P32(DD, 0x210u) = C32(DS, 0x210u);
    P32(DD, 0x214u) = C32(g2_dashboard_sched_src_200743fc, 0x220u);
#undef DD
#undef DS
    P8(parsed, PARSED_HAS_SCHEDULE) = 1u;
}

/* widget data: pb oneof {which u16 +0: 1 news (legacy), 2 stock, 3 schedule;
 * body +8}. Unknown kinds are ignored. Returns 0 only for NULL args. */
uint32_t dashboard_parse_widget_data_4fdad4(const uint8_t *widget, uint8_t *parsed)
{
    if (widget == NULL || parsed == NULL)
        return 0u;
    switch (C16(widget, 0u)) {
    case 1u:
        parse_news(widget + 8, parsed);
        break;
    case 2u:
        parse_stock(widget + 8, parsed);
        break;
    case 3u:
        parse_schedule(widget + 8, parsed);
        break;
    default:
        break;
    }
    return 1u;
}

void clear_news_cache_data_to_disp_buffer_4fdf08(void)
{
    DP_LOG(3u, fn_clear, 0x192u, 0u, m_clear, t_clear);
    (void)osMutexAcquire(g2_dashboard_mutex_200743a8, WAIT_FOREVER);
    (void)aeabi_memset_43c0e4(g2_news_staging_203024a4, sizeof g2_news_staging_203024a4, 0);
    (void)osMutexRelease(g2_dashboard_mutex_200743a8);
}

/* Copies every valid staged session into the matching display slot (invalid
 * slots are left as they are). 1 = done, 0 = NULL buffer. */
uint32_t load_news_cache_data_to_disp_buffer_4fdf74(uint8_t *news_widget_data)
{
    const g2_news_session_t *s;
    g2_news_disp_record_t *d;

    if (news_widget_data == NULL) {
        DP_LOG(1u, fn_load, 0x19du, 0u, m_load_null, t_load_null);
        return 0u;
    }
    (void)osMutexAcquire(g2_dashboard_mutex_200743a8, WAIT_FOREVER);
    for (int32_t i = 0; i < (int32_t)NEWS_SLOTS; i++) {
        s = (const g2_news_session_t *)(const void *)(g2_news_staging_203024a4 +
                                                      (uint32_t)i * sizeof(g2_news_session_t));
        if (s->valid != 1u)
            continue;
        d = (g2_news_disp_record_t *)(void *)(news_widget_data +
                                              (uint32_t)i * sizeof(g2_news_disp_record_t));
        d->valid = 1u;
        d->news_id = s->news_id;
        d->stamp[0] = s->stamp[0];
        d->stamp[1] = s->stamp[1];
        (void)audio_settings_copy_text(d->source, s->text_14, 0x7fu);
        d->source[0x7f] = '\0';
        (void)audio_settings_copy_text(d->title, s->text_94, 0x7fu);
        d->title[0x7f] = '\0';
        (void)audio_settings_copy_text(d->body, s->body, 0x1b89u);
        d->body[0x1b89] = '\0';
    }
    (void)osMutexRelease(g2_dashboard_mutex_200743a8);
    return 1u;
}
