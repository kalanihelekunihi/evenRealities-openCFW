/* SPDX-License-Identifier: MIT */
/* Recovered ordered SPI-master insertion and first eligible flash binding. */
typedef __UINTPTR_TYPE__ uintptr_t;
#include <driver/spi.h>
_Static_assert(__builtin_offsetof(struct spi_master, list) == 28, "SPI master ABI");
_Static_assert(__builtin_offsetof(struct sflash_master, list) == 24, "SPI flash ABI");
extern volatile struct list_head open_cfw_gx8002_device_heads[2];
int open_cfw_gx8002_spi_register_master(struct spi_master *master)
{
    if (!master) return -19;
    volatile struct spi_master *m = master;
    unsigned int selects = m->num_chipselect;
    if (!selects) return -22;
    int bus = m->bus_num;
    if (bus < 0) return -22;
    volatile struct list_head *head = &open_cfw_gx8002_device_heads[0];
    struct list_head *entry = &master->list;
    volatile struct list_head *previous = head->prev;
    m->list.next = (struct list_head *)head;
    head->prev = entry;
    m->list.prev = (struct list_head *)previous;
    previous->next = entry;
    volatile struct list_head *flash_head = &open_cfw_gx8002_device_heads[1];
    volatile struct list_head *node = flash_head->next;
    for (;;) {
        struct list_head *next = node->next;
        if (node == flash_head) break;
        volatile struct sflash_master *flash = (volatile struct sflash_master *)
            ((uintptr_t)node - __builtin_offsetof(struct sflash_master, list));
        if (flash->bus_num == bus && flash->spi.chip_select < selects) {
            flash->spi.master = master;
            break;
        }
        node = next;
    }
    return 0;
}
