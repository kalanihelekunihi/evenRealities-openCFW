/* SPDX-License-Identifier: MIT */
/* Reconstructed transfer candidate. Not admitted until decoded qualification. */
#include <driver/spi.h>
typedef __UINTPTR_TYPE__ uintptr_t;
extern void open_cfw_gx8002_clock_gate(unsigned int, unsigned int);
struct dw_transfer_state {
    struct spi_master *master;
    volatile unsigned int *registers;
    unsigned int tx_depth, rx_depth;
    struct spi_message *message;
    struct spi_transfer *transfer;
    void *buffer;
    unsigned int length, cleared_word, unknown_word;
    unsigned char width;
};
struct dw_device_state {
    struct spi_device *device;
    unsigned int control, divider, transfer_mode;
};
_Static_assert(__builtin_offsetof(struct dw_transfer_state, width)==40,"DW width ABI");
_Static_assert(__builtin_offsetof(struct spi_transfer, transfer_list)==24,"SPI list ABI");

int open_cfw_gx8002_dw_spi_quick_transfer(struct spi_device *device,
                                        struct spi_message *message)
{
    volatile struct spi_device *d=device;
    volatile struct spi_master *master=d->master;
    volatile struct dw_transfer_state *state=master->driver_data;
    volatile struct spi_message *m=message;
    int result=0;
    m->actual_length=0;
    struct spi_message *active=state->message;
    m->spi=device;
    if (active) goto finish;
    state->message=message;
    open_cfw_gx8002_clock_gate(14,1);
    *(volatile unsigned int *)(uintptr_t)0xa030008cu=2;
    volatile struct spi_message *current=state->message;
    struct list_head *node=current->transfers.next;
    while (1) {
        if (node==(struct list_head *)current) break;
        volatile struct spi_transfer *transfer=(void *)((uintptr_t)node-24u);
        volatile struct spi_device *spi=current->spi;
        const void *buffer=transfer->tx_buf;
        state->transfer=(struct spi_transfer *)transfer;
        volatile struct dw_device_state *config=spi->controller_state;
        if (!buffer) buffer=transfer->rx_buf;
        unsigned int length=transfer->len;
        state->buffer=(void *)buffer;
        state->length=length;
        unsigned int bits=transfer->bits_per_word;
        if (!bits) {
            transfer->bits_per_word=8;
            state->width=1;
        } else {
            unsigned int rounded=(bits+7u)&248u;
            if (rounded==24) rounded=32;
            state->width=rounded>>3;
        }
        const void *tx=transfer->tx_buf;
        bits=transfer->bits_per_word;
        unsigned int control=(bits-1u)|config->control;
        state->registers[2]=0;
        volatile unsigned int *mode_registers=state->registers;
        unsigned int transfer_mode=config->transfer_mode;
        mode_registers[60]=transfer_mode;
        state->registers[0]=control|(tx?1024u:2048u);
        unsigned int divider=config->divider&65535u;
        state->registers[5]=divider<2?2:divider;
        state->registers[1]=0;
        state->registers[19]=0;
        unsigned int width=state->width;
        length=state->length;
        unsigned int remaining=length/width;
        unsigned int mask=state->rx_depth*2u-1u;
        if (length%width || (uintptr_t)buffer%width) {
            result=-22;
            goto shutdown;
        }
        volatile unsigned int *aligned_registers=state->registers;
        state->cleared_word=0;
        aligned_registers[2]=0;
        state->registers[4]=1;
        state->registers[19]=0;
        uintptr_t cursor=(uintptr_t)buffer;
        volatile unsigned int *end_registers;
        if (tx) {
            state->registers[2]=1;
            while (remaining) {
                volatile unsigned int *regs=state->registers;
                unsigned int used=regs[8]&mask;
                unsigned int free_words=state->tx_depth-used;
                int count=(int)free_words<(int)remaining?(int)free_words:(int)remaining;
                regs[1]=(unsigned int)count-1u;
                for (unsigned int i=0;i!=(unsigned int)count;++i) {
                    if (width==1) {
                        unsigned int word=((const volatile unsigned char *)cursor)[i];
                        volatile unsigned int *data_registers=state->registers;
                        data_registers[24]=word;
                    }
                    else if (width==2) { volatile unsigned int *data_registers=state->registers; unsigned int word=((const volatile unsigned short *)cursor)[i]; data_registers[24]=word; }
                    else if (width==4) state->registers[24]=((const unsigned int *)cursor)[i];
                }
                if (width==1 || width==2 || width==4) cursor+=(unsigned int)count*width;
                remaining-=(unsigned int)count;
            }
            end_registers=state->registers;
            volatile unsigned int *status=end_registers+10;
            while (!(*status&4u)) {}
            while (*status&1u) {}
        } else {
            end_registers=state->registers;
            while (remaining) {
                end_registers[2]=0;
                unsigned int depth=state->rx_depth;
                volatile unsigned int *regs=state->registers;
                unsigned int count=remaining<depth?remaining:depth;
                regs[1]=count-1u;
                unsigned int pending=count;
                state->registers[2]=1;
                state->registers[24]=0;
                end_registers=state->registers;
                while (pending) {
                    unsigned int available=end_registers[9]&mask;
                    for (int i=0;i<(int)available;++i) {
                        if (width==1) { *(unsigned char *)cursor=end_registers[24]; cursor+=1; end_registers=state->registers; }
                        else if (width==2) { *(unsigned short *)cursor=end_registers[24]; cursor+=2; }
                        else if (width==4) { *(unsigned int *)cursor=end_registers[24]; cursor+=4; end_registers=state->registers; }
                    }
                    pending-=available;
                }
                remaining-=count;
            }
        }
        node=((volatile struct list_head *)node)->next;
        current=state->message;
        end_registers[2]=0;
    }
shutdown:
    *(volatile unsigned int *)(uintptr_t)0xa030008cu=3;
    open_cfw_gx8002_clock_gate(14,0);
finish:
    state->message=0;
    state->transfer=0;
    return result;
}
