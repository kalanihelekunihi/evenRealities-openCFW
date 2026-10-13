#include <stdint.h>
extern void audio_uart_nema_error_set_4b127c(uint32_t);
extern void audio_uart_nema_buffer_flush_5140ea(void *);
extern uint32_t audio_uart_nema_reg_read_51403c(uint32_t);
extern int32_t audio_uart_nema_poll_514026(uint32_t);
extern uint32_t audio_uart_nema_sector_finalize_523ce0(uint32_t,uint32_t);
extern uint32_t audio_uart_nema_chain_finalize_523dba(void *,uint32_t);
static int32_t finalize_divide(int32_t a,int32_t b) {
    if(b==0)return 0;
    if(a==INT32_MIN && b==-1)return INT32_MIN;
    return a/b;
}
static void finalize_flush_sector(volatile uint32_t *list,uint32_t data) {
    uint32_t offset=list[12]*list[11];
    uint32_t physical=list[3]+offset*4u;
    uint32_t descriptor[4];
    descriptor[3]=physical;descriptor[2]=data+offset*4u;
    descriptor[0]=list[11]*4u;descriptor[1]=list[1];
    audio_uart_nema_buffer_flush_5140ea(descriptor);
}
/* Native514b7c..514cf2: sector finalization and chained-buffer flush/link policy. */
void audio_uart_nema_list_finalize_514b7c(void *cell) {
    volatile uint32_t *root=(volatile uint32_t *)cell;
    if(!root) {audio_uart_nema_error_set_4b127c(8192u);return;}
    uint32_t flags=root[6],used=root[5];
    if(flags&32u) {
        uint32_t sector=root[11];
        uint32_t residue=used-sector*(uint32_t)finalize_divide((int32_t)used,(int32_t)sector);
        if(residue==0u)return;
        uint32_t offset=sector*root[12];
        uint32_t physical=root[3]+offset*4u;
        if(!(flags&8u)) {
            uint32_t virtual_address=root[2]+offset*4u;
            uint32_t descriptor[4]={root[11]*4u,root[1],virtual_address,physical};
            audio_uart_nema_buffer_flush_5140ea(descriptor);
            root[6]=root[6]|8u;
        }
        uint32_t submitted=audio_uart_nema_reg_read_51403c(328u);
        uint32_t capacity=root[10],sequence=root[13];
        root[14]=submitted;
        if((int32_t)(sequence-submitted)>(int32_t)(capacity-2u))
            (void)audio_uart_nema_poll_514026(submitted+1u);
        root[13]=audio_uart_nema_sector_finalize_523ce0(physical,residue);
        uint32_t position=root[12]+1u;
        capacity=root[10];
        uint32_t next_used;
        if(position>=capacity) {position=0u;next_used=0u;}
        else next_used=root[11]*position;
        root[5]=next_used;root[12]=position;
        return;
    }
    if(used==0u)return;
    volatile uint32_t *list=root;
    for(;;) {
        uint32_t byteflags=((volatile uint8_t *)list)[24];
        uint32_t data=list[2];
        volatile uint32_t *next=(volatile uint32_t *)(uintptr_t)list[8];
        if(byteflags&4u) {
            if(next) {
                uint32_t capacity=list[4],next_used=next[5];
                *(volatile uint32_t *)(uintptr_t)(data+capacity*4u-4u)=next_used;
            }
            flags=list[6]&~8u;list[6]=flags;
            if(flags&32u)finalize_flush_sector(list,data);
            else audio_uart_nema_buffer_flush_5140ea((void *)list);
            list[6]=list[6]|8u;
            list=(volatile uint32_t *)(uintptr_t)list[8];
            if(list)continue;
            break;
        }
        flags=list[6];
        if(flags&8u)break;
        if(flags&32u) {
            /* Native branch re-reads virtual pointer after physical pointer. */
            uint32_t offset=list[12]*list[11];
            uint32_t physical=list[3]+offset*4u;
            uint32_t virtual_address=list[2]+offset*4u;
            uint32_t descriptor[4]={list[11]*4u,list[1],virtual_address,physical};
            audio_uart_nema_buffer_flush_5140ea(descriptor);
        } else audio_uart_nema_buffer_flush_5140ea((void *)list);
        list[6]=list[6]|8u;
        break;
    }
    root[7]=audio_uart_nema_chain_finalize_523dba(cell,root[5]);
}
