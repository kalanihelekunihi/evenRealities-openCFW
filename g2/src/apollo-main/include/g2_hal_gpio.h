/* Product GPIO HAL (stock native 0x53a414..0x53a651, presumably
 * driver\hal\src\hal_gpio.c next to hal_i2c.c; no path string survives). */
#ifndef G2_HAL_GPIO_H
#define G2_HAL_GPIO_H
#include <stdint.h>

/* One row of the board pin table (ROM 0x686db8, 0x61 rows). */
typedef struct {
    uint32_t pin;            /* +0x0 Apollo GPIO number */
    uint8_t mode;            /* +0x4 G2_GPIO_MODE_* */
    uint8_t level;           /* +0x5 initial output level (1 = high) */
    uint8_t int_dir;         /* +0x6 0 = no IRQ, else am_hal_gpio eIntDir (1..3) */
    uint8_t reserved;        /* +0x7 */
    void (*handler)(void *); /* +0x8 am_hal_gpio_handler_t, registered on channel 0 */
} g2_gpio_row_t;
_Static_assert(sizeof(g2_gpio_row_t) == 12, "stock GPIO table row is 12 bytes");

enum {
    G2_GPIO_MODE_OUTPUT = 1u,
    G2_GPIO_MODE_INPUT = 2u,
    G2_GPIO_MODE_DISABLED = 4u,
};

/* Configure `rows` table rows; -1 if table is NULL or rows is 0, else 0. */
int32_t board_gpio_table_init_53a454(const void *table, uint32_t rows);
/* Read the input level of `pin` into *level (0/1); 0 ok, -1 HAL error. */
int32_t hal_gpio_input_get_53a590(uint32_t pin, uint8_t *level);

#endif
