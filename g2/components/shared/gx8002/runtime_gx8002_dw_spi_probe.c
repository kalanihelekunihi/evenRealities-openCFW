/* SPDX-License-Identifier: MIT */
/* Recovered initialization sequence; hardware probing remains unqualified. */
#include <driver/spi.h>
typedef __UINTPTR_TYPE__ uintptr_t;
extern void open_cfw_gx8002_clock_gate(unsigned int, unsigned int);
extern int open_cfw_gx8002_spi_register_master(struct spi_master *);
extern void open_cfw_gx8002_request_irq(unsigned int, int (*)(int,void *), void *);
extern void open_cfw_gx8002_dw_spi_cleanup(struct spi_device *);
extern int open_cfw_gx8002_dw_spi_setup(struct spi_device *);
extern int open_cfw_gx8002_dw_spi_quick_transfer(struct spi_device *,struct spi_message *);
extern int open_cfw_gx8002_dw_spi_irq(int,void *);
struct open_cfw_dw_spi_probe_state {
    struct spi_master *master;
    volatile unsigned int *registers;
    unsigned int tx_depth;
    unsigned int rx_depth;
    struct spi_message *message;
    struct spi_transfer *transfer;
};
_Static_assert(__builtin_offsetof(struct open_cfw_dw_spi_probe_state, message)==16,"DW message ABI");

void open_cfw_gx8002_dw_spi_probe(void)
{
    volatile struct spi_master *master=(void *)(uintptr_t)0x20027af0u;
    volatile struct open_cfw_dw_spi_probe_state *state=(void *)(uintptr_t)0x20027b14u;
    state->registers=(void *)(uintptr_t)0xa3000000u;
    state->master=(struct spi_master *)master;
    master->driver_data=(void *)state;
    master->bus_num=0;
    master->num_chipselect=1;
    master->cleanup=open_cfw_gx8002_dw_spi_cleanup;
    master->setup=open_cfw_gx8002_dw_spi_setup;
    master->transfer=open_cfw_gx8002_dw_spi_quick_transfer;
    open_cfw_gx8002_clock_gate(14,1);
    state->registers[2]=0;
    state->registers[11]=78;
    if (state->tx_depth==0) {
        unsigned int value=2,remaining=256;
        volatile unsigned int *threshold;
        do {
            state->registers[6]=value;
            volatile unsigned int *registers=state->registers;
            threshold=registers+6;
            if (registers[6]!=value) {
                if (value==257) value=0;
                break;
            }
            ++value;
        } while (--remaining);
        state->tx_depth=value;
        *threshold=0;
    }
    if (state->rx_depth==0) {
        unsigned int value=2,remaining=256;
        volatile unsigned int *threshold;
        do {
            state->registers[7]=value;
            volatile unsigned int *registers=state->registers;
            threshold=registers+7;
            if (registers[7]!=value) {
                if (value==257) value=0;
                break;
            }
            ++value;
        } while (--remaining);
        state->rx_depth=value;
        *threshold=0;
    }
    *(volatile unsigned int *)(uintptr_t)0xa030008cu=3;
    state->registers[2]=1;
    volatile unsigned int *registers=state->registers;
    while (registers[10]&8u)
        (void)registers[24];
    while (registers[10]&1u) {}
    open_cfw_gx8002_clock_gate(14,0);
    state->message=0;
    state->transfer=0;
    (void)open_cfw_gx8002_spi_register_master((struct spi_master *)master);
    open_cfw_gx8002_request_irq(16,open_cfw_gx8002_dw_spi_irq,(void *)state);
}
