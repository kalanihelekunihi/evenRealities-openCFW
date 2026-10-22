/* Lightweight ring buffer (Tilen Majerle lwrb v3.x, MIT; not pinned under
 * third-party/upstream), module native 0x46d8a0..0x46db04.
 * This unit holds lwrb_init (0x46d8a0) and lwrb_read_ex (0x46d9c8). The other members of
 * the module already exist in g2/src under product names: lwrb_write 0x46d8c4 /
 * lwrb_write_ex 0x46d8e0 / lwrb_get_free 0x46da92 (app/input-ring/input_ring_write.c),
 * lwrb_read 0x46d9ac with lwrb_read_ex folded in / lwrb_get_full 0x46dacc
 * (drivers/peripherals/ring-read/display_ring_read.c).
 * Stock is built with C11 atomics: the read index is loaded with LDA and stored with STL. */
#include <stdint.h>
#include <stddef.h>

typedef struct g2_lwrb g2_lwrb_t;
typedef void (*g2_lwrb_evt_fn)(g2_lwrb_t *buff, uint32_t evt, uint32_t bp);

struct g2_lwrb {
    uint8_t *buff;          /* +0x00 */
    uint32_t size;          /* +0x04 */
    uint32_t r;             /* +0x08 read index (atomic) */
    uint32_t w;             /* +0x0c write index (atomic) */
    g2_lwrb_evt_fn evt_fn;  /* +0x10 */
};
_Static_assert(sizeof(g2_lwrb_t) == 0x14, "lwrb_t");

enum { LWRB_EVT_READ = 0u, LWRB_EVT_WRITE = 1u, LWRB_FLAG_READ_ALL = 1u };

extern uint32_t audio_uart_display_ring_available(const void *descriptor); /* 0x46dacc lwrb_get_full */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* 0x439be4 memcpy */

uint8_t lwrb_init_46d8a0(g2_lwrb_t *buff, void *buffdata, uint32_t size)
{
    if (buff == NULL || buffdata == NULL || size == 0u)
        return 0u;
    buff->evt_fn = NULL;
    buff->size = size;
    buff->buff = buffdata;
    buff->w = 0u;
    buff->r = 0u;
    return 1u;
}

uint8_t lwrb_read_ex_46d9c8(g2_lwrb_t *buff, void *data, uint32_t btr, uint32_t *br, uint16_t flags)
{
    uint8_t *d = data;
    if (buff == NULL || buff->buff == NULL || buff->size == 0u || data == NULL || btr == 0u)
        return 0u;
    uint32_t full = audio_uart_display_ring_available(buff);
    if (full == 0u || (full < btr && (flags & LWRB_FLAG_READ_ALL) != 0u))
        return 0u;
    if (full < btr)
        btr = full;
    uint32_t r = __atomic_load_n(&buff->r, __ATOMIC_ACQUIRE);
    uint32_t tocopy = buff->size - r < btr ? buff->size - r : btr;
    (void)audio_queue_copy_bytes(d, buff->buff + r, tocopy);
    d += tocopy;
    r += tocopy;
    btr -= tocopy;
    if (btr > 0u) {
        (void)audio_queue_copy_bytes(d, buff->buff, btr);
        r = btr;
    }
    if (r >= buff->size)
        r = 0u;
    __atomic_store_n(&buff->r, r, __ATOMIC_RELEASE);
    if (buff->evt_fn != NULL)
        buff->evt_fn(buff, LWRB_EVT_READ, tocopy + btr);
    if (br != NULL)
        *br = tocopy + btr;
    return 1u;
}
