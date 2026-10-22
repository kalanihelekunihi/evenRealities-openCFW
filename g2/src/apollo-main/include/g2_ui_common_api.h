/* UI common API (stock D:\01_workspace\s200_ap510b_iar_git\app\gui\common\ui_common_api.c,
 * native 0x509c1c..0x509f97): the per-page byte event FIFO and small page
 * helpers shared by the dashboard, onboarding, Even AI, stock, calendar,
 * news and EvenHub container pages.
 *
 * The FIFO is a 0x206-byte heap block: a 512-byte ring followed by the write
 * index, read index and byte count (all uint16_t). Return codes: -4 fifo is
 * NULL, -3 data/buffer NULL or length 0, -1 not enough free space. */
#ifndef G2_UI_COMMON_API_H
#define G2_UI_COMMON_API_H

#include <stdint.h>

#define G2_UI_FIFO_SIZE 0x200 /* int: the stock index wrap is a signed modulo */

typedef struct {
    uint8_t buf[G2_UI_FIFO_SIZE]; /* +0x000 */
    uint16_t head;                /* +0x200 write index */
    uint16_t tail;                /* +0x202 read index */
    uint16_t count;               /* +0x204 bytes queued */
} g2_ui_fifo_t;
_Static_assert(sizeof(g2_ui_fifo_t) == 0x206u, "stock fifo block is 0x206 bytes");

g2_ui_fifo_t *ui_common_api_fn_00509c1c(void);                                     /* fifo_create */
void ui_common_api_fn_00509c96(g2_ui_fifo_t *fifo);                                 /* fifo_destroy */
int32_t ui_common_api_fn_00509ca2(g2_ui_fifo_t *fifo, const uint8_t *data, uint16_t len); /* fifo_push */
int32_t ui_common_api_fn_00509dfa(const g2_ui_fifo_t *fifo);                        /* 1 empty, 0 data */
int32_t ui_common_api_fn_00509e14(g2_ui_fifo_t *fifo, uint8_t *buffer, uint16_t max_len); /* fifo_pop */
void ui_common_api_fn_00509f52(g2_ui_fifo_t *fifo);                                 /* fifo_reset */
int32_t ui_common_api_fn_00509f7a(int32_t *x, int32_t *y);                          /* page offset (0, 0) */
uint32_t ui_common_api_fn_00509f86(void);                                           /* unread ANCC count */
uint8_t ui_common_api_fn_00509f8e(void);                                            /* battery percent */

#endif
