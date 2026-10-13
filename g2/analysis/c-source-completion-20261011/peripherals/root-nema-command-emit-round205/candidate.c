#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[];
extern void audio_uart_nema_register_emit_523e92(uint32_t,uint32_t);
extern void audio_uart_nema_sector_rollover_5147b0(void *);
extern void audio_uart_nema_error_set_4b127c(uint32_t);
extern void *audio_uart_nema_node_allocate_51416c(uint32_t);
extern void audio_uart_nema_buffer_create_514070(uint32_t *,uint32_t,uint32_t);
extern void audio_uart_nema_cl_node_release_514178(void *);
extern void audio_uart_nema_cl_unbind_5144ba(void);
static int32_t emit_signed_div(int32_t x,int32_t y) {
    if(y==0) return 0;
    if(x==INT32_MIN && y==-1) return INT32_MIN;
    return x/y;
}
static int32_t emit_space(volatile uint32_t *list) {
    uint32_t delta;
    if(((volatile uint8_t *)list)[24]&32u) {
        uint32_t sector=list[11],used=list[5];
        delta=sector-used+sector*(uint32_t)emit_signed_div((int32_t)used,(int32_t)sector);
    } else { uint32_t capacity=list[4],used=list[5];delta=capacity-used; }
    return (int32_t)delta/2;
}
static void emit_store(uint32_t base,uint32_t index,uint32_t value) {
    *(volatile uint32_t *)(uintptr_t)(base+index*4u)=value;
}
static void emit_pair(volatile uint32_t *list,uint32_t first,uint32_t second) {
    uint32_t used=list[5];
    emit_store(list[2],used,first);
    ++used;
    emit_store(list[2],used,second);
    list[5]=used+1u;
}
/* Native514846..514aec. Full sector/padding/allocation/chaining paths. */
void audio_uart_nema_child_514846(uint32_t reg,uint32_t value) {
    volatile uint32_t *context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
    volatile uint32_t *list=(void *)(uintptr_t)context[1];
    if(!list) { audio_uart_nema_register_emit_523e92(reg,value);return; }
    list[6]=list[6]&~8u;
    int32_t available=emit_space(list);
    uint32_t flags=list[6];
    if(flags&32u) {
        if(available<=1) {
            ((volatile uint8_t *)context)[249]=0u;
            context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
            audio_uart_nema_sector_rollover_5147b0((void *)(uintptr_t)context[1]);
        }
    } else if(!(flags&2u)) {
        uint32_t used=list[5],capacity=list[4];
        if((int32_t)capacity<(int32_t)(used+2u)) {audio_uart_nema_error_set_4b127c(8u);return;}
    } else {
        uint32_t used=list[5],capacity=list[4];
        if((int32_t)(used+4u)>=(int32_t)capacity) {
            int32_t padding=(int32_t)((uint32_t)emit_space(list)-2u);
            if(padding>0) {
                uint32_t n=(uint32_t)padding;
                for(uint32_t i=0;i<(n&3u);++i) emit_pair(list,0x10000u,0u);
                for(uint32_t i=0;i<(n>>2);++i) {
                    uint32_t k=list[5];
                    emit_store(list[2],k,0x10000u);++k;
                    emit_store(list[2],k,0u);++k;
                    uint32_t data=list[2];list[5]=k;
                    emit_store(data,k,0x10000u);++k;
                    emit_store(list[2],k,0u);++k;
                    data=list[2];list[5]=k;
                    emit_store(data,k,0x10000u);++k;
                    emit_store(list[2],k,0u);++k;
                    data=list[2];list[5]=k;
                    emit_store(data,k,0x10000u);++k;
                    emit_store(list[2],k,0u);list[5]=k+1u;
                }
            }
            volatile uint32_t *node=(void *)(uintptr_t)list[8];
            if(!node) {
                node=audio_uart_nema_node_allocate_51416c(60u);
                if(!node) {audio_uart_nema_error_set_4b127c(16u);return;}
                uint32_t desc[4];audio_uart_nema_buffer_create_514070(desc,0u,1024u);
                node[0]=desc[0];node[1]=desc[1];node[2]=desc[2];node[3]=desc[3];
                node[4]=(uint32_t)((int32_t)desc[0]/8)*2u;
                node[5]=0u;node[7]=UINT32_MAX;node[13]=UINT32_MAX;node[14]=UINT32_MAX;node[6]=2u;
                uint32_t data=node[2];
                node[8]=0u;node[9]=0u;node[10]=0u;node[11]=0u;node[12]=0u;
                if(!data) {audio_uart_nema_error_set_4b127c(16u);audio_uart_nema_cl_node_release_514178((void *)node);return;}
                context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
                list=(void *)(uintptr_t)context[1];
                uint32_t root=list[9];node[9]=root?root:(uint32_t)(uintptr_t)list;
                list=(void *)(uintptr_t)context[1];node[6]=list[6]&~12u;
            }
            context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
            list=(void *)(uintptr_t)context[1];
            if(!list) audio_uart_nema_error_set_4b127c(8192u);
            else list[6]=list[6]|4u;
            context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
            list=(void *)(uintptr_t)context[1];
            uint32_t k=list[5];
            emit_store(list[2],k,240u);++k;
            uint32_t address=node[3];emit_store(list[2],k,address);++k;
            uint32_t data=list[2];list[5]=k;
            emit_store(data,k,244u);++k;
            uint32_t capacity_next=node[4];emit_store(list[2],k,capacity_next);list[5]=k+1u;list[8]=(uint32_t)(uintptr_t)node;
            if(!node) audio_uart_nema_error_set_4b127c(8192u);
            else if(((volatile uint8_t *)node)[12]&7u) audio_uart_nema_error_set_4b127c(16384u);
            else {
                if(context[1]) audio_uart_nema_cl_unbind_5144ba();
                while(((volatile uint8_t *)node)[24]&4u) node=(void *)(uintptr_t)node[8];
                context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];context[1]=(uint32_t)(uintptr_t)node;
            }
        }
    }
    context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
    list=(void *)(uintptr_t)context[1];
    emit_pair(list,reg,value);
}
