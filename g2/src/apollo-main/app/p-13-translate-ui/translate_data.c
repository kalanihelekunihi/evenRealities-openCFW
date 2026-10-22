/* D:\01_workspace\s200_ap510b_iar_git\app\gui\translate\translate_data.c
 * (module "translate.data"), firmware 2.2.6.10, native 0x59e6d0..0x59e9e2.
 *
 * translate_data_update keeps the last four recognised/translated segments in
 * a ring (RAM 0x20119f00) and rebuilds the concatenated source and
 * destination display strings (RAM 0x2011bf14 / 0x2011cf1c, lengths at
 * 0x20074af4 / 0x20074af8). A segment that arrived with endFlag 1 is
 * finalised by the next update: a '\n' is appended to both of its texts and
 * the ring advances; otherwise the current slot is overwritten in place.
 *
 * Quirk kept from stock: the newline is appended while len < 0x401, so a slot
 * already holding 0x400 bytes writes one byte past its text into the next
 * slot's length field. */
#include <stddef.h>
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void audio_uart_checksum_copy(void *destination, const void *source,
                                     uint32_t length); /* 0x439be4 AEABI copy */

#define TRANSLATE_TEXT_MAX 0x400u
#define TRANSLATE_RING_SLOTS 4

typedef struct {
    uint16_t src_len;                    /* +0x000 */
    char src_text[TRANSLATE_TEXT_MAX];   /* +0x002 */
    uint16_t dst_len;                    /* +0x402 */
    char dst_text[TRANSLATE_TEXT_MAX];   /* +0x404 */
    uint8_t reserved804[4];              /* +0x804 not read here */
    uint32_t end_flag;                   /* +0x808 1 = segment final */
} translate_data_t;
_Static_assert(offsetof(translate_data_t, dst_len) == 0x402, "dst_len");
_Static_assert(offsetof(translate_data_t, end_flag) == 0x808, "end_flag");

typedef struct {
    uint16_t len;
    char text[TRANSLATE_TEXT_MAX];
} translate_text_slot_t;
_Static_assert(sizeof(translate_text_slot_t) == 0x402, "slot");

typedef struct {
    translate_text_slot_t src[TRANSLATE_RING_SLOTS];   /* +0x0000 */
    translate_text_slot_t dst[TRANSLATE_RING_SLOTS];   /* +0x1008 */
    uint8_t index;                                     /* +0x2010 newest slot */
    uint8_t pad[1];
} translate_text_ring_t;
_Static_assert(offsetof(translate_text_ring_t, dst) == 0x1008, "ring dst");
_Static_assert(offsetof(translate_text_ring_t, index) == 0x2010, "ring index");
_Static_assert(sizeof(translate_text_ring_t) == 0x2012, "ring"); /* cleared by 0x59e9e2 */

extern translate_text_ring_t g2_translate_text_ring;   /* RAM 0x20119f00 */
extern uint8_t g2_translate_segment_ended;             /* RAM 0x20075039 */
extern char g2_translate_src_display[0x1008];          /* RAM 0x2011bf14 */
extern uint32_t g2_translate_src_display_len;          /* RAM 0x20074af4 */
extern char g2_translate_dst_display[0x1008];          /* RAM 0x2011cf1c */
extern uint32_t g2_translate_dst_display_len;          /* RAM 0x20074af8 */

static const char module[] = "translate.data"; /* ROM 0x789c40 */
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\translate\\translate_data.c"; /* ROM 0x6fe594 */
static const char function[] = "translate_data_update"; /* ROM 0x77cf1c */
static const char m_null[] = "translate_data is NULL"; /* ROM 0x77cf34 */
static const char s_null[] = "[translate.data]translate_data is NULL"; /* ROM 0x7503c4 */
static const char m_end[] = "endFlag: %d"; /* ROM 0x78c794 */
static const char s_end[] = "[translate.data]endFlag: %d"; /* ROM 0x773afc */
static const char m_src[] = "src_text(len: %d): %s"; /* ROM 0x77cf4c */
static const char s_src[] = "[translate.data]src_text(len: %d): %s"; /* ROM 0x7503ec */
static const char m_dst[] = "dst_text(len: %d): %s"; /* ROM 0x77cf64 */
static const char s_dst[] = "[translate.data]dst_text(len: %d): %s"; /* ROM 0x750414 */
static const char m_done[] = "Translate data updated successfully"; /* ROM 0x75bf1c */
static const char s_done[] = "[translate.data]Translate data updated successfully"; /* ROM 0x72f878 */

#define TDATA_LOG(level, line, mask, msg, short_msg, ...)                         \
    do {                                                                          \
        if ((audio_log_flags() & 2u) != 0u)                                       \
            audio_log_extended((level), module, path, function, (line), (msg),    \
                               ##__VA_ARGS__);                                    \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)     \
            (void)compress_log_output((mask), (short_msg), (short_msg),           \
                                      ##__VA_ARGS__);                             \
    } while (0)

static void append_newline(translate_text_slot_t *slot)
{
    if (slot->len < TRANSLATE_TEXT_MAX + 1u) {
        ((char *)slot)[2u + slot->len] = '\n';
        slot->len++;
    }
}

void translate_data_update_59e6d0(const translate_data_t *data)
{
    translate_text_ring_t *ring = &g2_translate_text_ring;
    translate_text_slot_t *src;
    translate_text_slot_t *dst;
    int i;

    if (data == NULL) {
        TDATA_LOG(1u, 0x21u, 0x04000000u, m_null, s_null);
        return;
    }
    TDATA_LOG(3u, 0x25u, 0x0c400000u, m_end, s_end, data->end_flag);
    if (data->end_flag == 1u) {
        TDATA_LOG(3u, 0x27u, 0x0c800000u, m_src, s_src, (uint32_t)data->src_len,
                  data->src_text);
        TDATA_LOG(3u, 0x28u, 0x0c800000u, m_dst, s_dst, (uint32_t)data->dst_len,
                  data->dst_text);
    }

    src = &ring->src[ring->index];
    dst = &ring->dst[ring->index];
    if (g2_translate_segment_ended == 1u) {
        g2_translate_segment_ended = 0u;
        append_newline(src);
        append_newline(dst);
        ring->index = (uint8_t)((ring->index + 1) % TRANSLATE_RING_SLOTS);
        src = &ring->src[ring->index];
        dst = &ring->dst[ring->index];
    }
    (void)aeabi_memset_43c0e4(src, sizeof(*src), 0);
    (void)aeabi_memset_43c0e4(dst, sizeof(*dst), 0);
    audio_uart_checksum_copy(src->text, data->src_text, data->src_len);
    src->len = data->src_len;
    audio_uart_checksum_copy(dst->text, data->dst_text, data->dst_len);
    dst->len = data->dst_len;
    if (data->end_flag == 1u)
        g2_translate_segment_ended = 1u;
    TDATA_LOG(4u, 0x51u, 0x10000000u, m_done, s_done);

    (void)aeabi_memset_43c0e4(g2_translate_src_display, sizeof(g2_translate_src_display), 0);
    g2_translate_src_display_len = 0u;
    (void)aeabi_memset_43c0e4(g2_translate_dst_display, sizeof(g2_translate_dst_display), 0);
    g2_translate_dst_display_len = 0u;
    /* Oldest to newest; a slot is skipped only when both texts are empty. */
    for (i = 0; i < TRANSLATE_RING_SLOTS; i++) {
        int slot = (ring->index + i + 1) % TRANSLATE_RING_SLOTS;

        src = &ring->src[slot];
        dst = &ring->dst[slot];
        if (src->len == 0u && dst->len == 0u)
            continue;
        audio_uart_checksum_copy(g2_translate_src_display + g2_translate_src_display_len,
                                 src->text, src->len);
        g2_translate_src_display_len += src->len;
        audio_uart_checksum_copy(g2_translate_dst_display + g2_translate_dst_display_len,
                                 dst->text, dst->len);
        g2_translate_dst_display_len += dst->len;
    }
}
