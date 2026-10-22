/* Stock source: D:\01_workspace\s200_ap510b_iar_git\app\gui\onboarding\ui_onboarding_news_page.c
 * Native 0x50af4c..0x50af86 (news FIFO init) and 0x50af86..0x50af94 (its
 * init-table entry, ROM 0x6d1ebc, priority 100; literal 0x50b728 =
 * 0x20120340). They sit in the gap between the a-41 halves of the TU
 * (ui/a-41-onboarding-news/ui_onboarding_news_page.c ends at 0x50af47 and
 * resumes with the FIFO pop at 0x50afa4); the pool words 0x50af94..0x50afa3
 * belong to that file. The init table refers to the entry as
 * g2_init_entry_50af86 (manifest defsym). */
#include <stdint.h>
#include <stddef.h>

#define NEWS_RECORD_SIZE 0xc88u
#define NEWS_FIFO_CAPACITY 10u

/* RAM 0x20120340 header as written by the init (same object as
 * g2_onboarding_news_fifo_t in ui_onboarding_news_page.c). */
typedef struct {
    uint16_t tail;          /* +0x00 write index */
    uint16_t head;          /* +0x02 read index */
    uint16_t count;         /* +0x04 */
    uint16_t record_size;   /* +0x06 0xc88 */
    uint16_t capacity;      /* +0x08 10 */
    uint8_t initialised;    /* +0x0a */
    uint8_t reserved_0b[5];
    uint8_t records[];      /* +0x10, capacity * record_size (0x7d50) bytes */
} g2_onboarding_news_fifo_header_t;
_Static_assert(offsetof(g2_onboarding_news_fifo_header_t, records) == 0x10u, "records at +0x10");

extern g2_onboarding_news_fifo_header_t g2_onboarding_news_fifo_20120340; /* RAM 0x20120340 */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* memset 0x43c0e4 */

/* Initialise once: empty ring of ten 0xc88-byte records, storage zeroed. */
void onboarding_news_page_fifo_init_50af4c(g2_onboarding_news_fifo_header_t *fifo)
{
    if (fifo == NULL || fifo->initialised != 0u)
        return;
    fifo->tail = 0u;
    fifo->head = 0u;
    fifo->count = 0u;
    fifo->record_size = (uint16_t)NEWS_RECORD_SIZE;
    fifo->capacity = (uint16_t)NEWS_FIFO_CAPACITY;
    audio_uart_buffer_zero(fifo->records, NEWS_FIFO_CAPACITY * NEWS_RECORD_SIZE, 0u);
    fifo->initialised = 1u;
}

int32_t onboarding_news_fifo_auto_init_50af86(void)
{
    onboarding_news_page_fifo_init_50af4c(&g2_onboarding_news_fifo_20120340);
    return 0;
}
