#include <stdint.h>

extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_pal_random_step(void);
extern uint32_t opencfw_em9305_init_transition_stage_318290(
    uintptr_t,uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_init_transition_stage_318348(
    uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_init_transition_record_323c78(
    uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t);
/* Native 327d16 captures input R3 (config+28) in the BL delay slot. */
extern uint32_t opencfw_em9305_init_transition_record_3239b8(
    uintptr_t,uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_radio_encode_3239d4(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_init_transition_segment_3243dc(
    uint32_t,uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_associated_object_init_312918(
    uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_auxiliary_insert_313220(uintptr_t);
extern uint32_t opencfw_em9305_init_transition_process_327de8(uintptr_t);
extern uint32_t opencfw_em9305_init_transition_callback_32805c(uintptr_t);
extern uint32_t opencfw_em9305_init_transition_callback_328018(uintptr_t,uintptr_t);

static uint32_t load32(const uint8_t *p)
{ return (uint32_t)p[0]|((uint32_t)p[1]<<8u)|
    ((uint32_t)p[2]<<16u)|((uint32_t)p[3]<<24u); }
static void store32(uint8_t *p,uint32_t v)
{ for(unsigned i=0;i<4u;i++)p[i]=(uint8_t)(v>>(i*8u)); }

/* Native 0x327b60..0x327dba. The ARC entry allocates the original 24-byte
 * frame; only fields actually written by native branches are initialized.
 * Child 3239b8's input R3 is captured before its call. */
uint32_t opencfw_em9305_init_transition_start_327b60_body(uint8_t *frame)
{
    uintptr_t flags=0x805a85u, config=0x805b84u;
    uint32_t feature=*(volatile uint8_t *)(flags+16u);
    uint32_t mode=*(volatile uint8_t *)(config+12u);
    frame[4]=0u;
    store32(frame,0u); /* Native branch delay slot, all paths. */
    if((feature&(1u<<6u))!=0u && mode<5u &&
       ((0x13u>>mode)&1u)!=0u) frame[1]=1u;

    uintptr_t root=0x8052d4u;
    uintptr_t active=root+44u;
    (void)opencfw_em9305_memset((void *)active,0u,204u);
    uintptr_t packet=root+92u;
    uint8_t sample=*(volatile uint8_t *)(flags+23u);
    *(volatile uint32_t *)(active+44u)=(uint32_t)packet;
    *(volatile uint8_t *)(active+26u)=1u;
    *(volatile uint8_t *)(active+24u)=2u;
    *(volatile uint8_t *)(active+48u)=3u;
    *(volatile uint32_t *)(active+32u)=
        (uint32_t)(uintptr_t)opencfw_em9305_init_transition_process_327de8;
    *(volatile uint32_t *)(active+28u)=
        (uint32_t)(uintptr_t)opencfw_em9305_init_transition_process_327de8;
    *(volatile uint16_t *)(active+60u)=257u;
    *(volatile uint32_t *)(active+56u)=0x00555555u;
    *(volatile uint32_t *)(active+52u)=0x8e89bed6u;
    *(volatile uint8_t *)(active+50u)=sample;
    if(mode!=1u && mode!=4u) {
        uint32_t select=*(volatile uint8_t *)(config+25u);
        if((select&3u)!=0u) {
            uint32_t mask=(select&2u)==0u?8u:((select&1u)!=0u?40u:32u);
            *(volatile uint16_t *)(uintptr_t)0x80537eu=(uint16_t)mask;
        }
    }
    uint32_t feature2=*(volatile uint8_t *)flags;
    uint8_t chooser=*(volatile uint8_t *)(config+24u);
    *(volatile uint8_t *)(uintptr_t)0x8053afu=chooser;
    uint32_t choice=0u;
    if((feature2&(1u<<6u))!=0u) {
        choice=opencfw_em9305_pal_random_step()%3u;
        mode=*(volatile uint8_t *)(config+12u);
    }
    *(volatile uint8_t *)(uintptr_t)0x8053aeu=(uint8_t)choice;
    if(mode>4u)return choice;

    uintptr_t half=0x80537cu;
    switch(mode) {
    case 0u:
        frame[0]=0u;
        *(volatile uint16_t *)half=40u;
        break;
    case 1u:
        *(volatile uint32_t *)(config+4u)=0u;
        *(volatile uint8_t *)(uintptr_t)0x8053aeu=0u;
        *(volatile uint32_t *)(config+8u)=0xea6u;
        *(volatile uint32_t *)config=0x138800u;
        frame[0]=1u;
        *(volatile uint16_t *)half=32u;
        break;
    case 2u:
        *(volatile uint16_t *)half=8u;
        frame[0]=6u;
        break;
    case 3u:
        frame[0]=2u;
        break;
    default: /* mode 4 */
        frame[0]=1u;
        *(volatile uint16_t *)half=32u;
        break;
    }

    uint32_t first5=*(volatile uint32_t *)(config+20u);
    uint32_t first4=*(volatile uint32_t *)(config+16u);
    uint32_t first3=*(volatile uint8_t *)(config+14u);
    uint32_t first2=*(volatile uint8_t *)(config+13u);
    (void)opencfw_em9305_init_transition_stage_318290(packet,
        (uintptr_t)frame,first2,first3,first4,first5,
        (uintptr_t)(frame+16u));
    uint32_t second4=*(volatile uint32_t *)(config+20u);
    uint32_t second3=*(volatile uint32_t *)(config+16u);
    uint32_t second2=*(volatile uint8_t *)(config+14u);
    store32(frame+12u,0u);
    store32(frame+8u,0u);
    (void)opencfw_em9305_init_transition_stage_318348(packet,0u,
        second2,second3,second4,(uintptr_t)(frame+8u));
    mode=*(volatile uint8_t *)(config+12u);
    uint32_t live=0u;
    uint32_t value16=load32(frame+16u),value20=load32(frame+20u);
    if(mode==1u || mode==4u) {
        uint32_t v12=load32(frame+12u),v8=load32(frame+8u);
        uint32_t all=v8|v12;
        uint32_t empty=(all==0u);
        uint32_t arg3=v8,arg4=v12;
        uint8_t kind=*(volatile uint8_t *)(config+14u);
        if(all==0u) {
            arg4=*(volatile uint32_t *)(config+20u);
            arg3=*(volatile uint32_t *)(config+16u);
        }
        frame[3]=(uint8_t)((!empty || kind!=0u)&1u);
        live=opencfw_em9305_init_transition_record_323c78(
            root+2u,value16,value20,arg3,arg4);
        frame[4]=(uint8_t)live;
        uintptr_t captured_root_record=root+2u; /* BL delay slot 327cf4. */
        uint32_t flags_word=*(volatile uint32_t *)(captured_root_record+170u);
        *(volatile uint32_t *)(captured_root_record+170u)=flags_word|4u;
    } else {
        uintptr_t config_record=config+28u;
        uintptr_t captured_record=config_record; /* Native BL delay slot. */
        live=opencfw_em9305_init_transition_record_3239b8(
            root+2u,value16,value20,config_record);
        *(volatile uint8_t *)(captured_record+32u)=0u;
        frame[4]=(uint8_t)live;
    }
    (void)opencfw_em9305_radio_encode_3239d4(root,(uintptr_t)frame);
    mode=*(volatile uint8_t *)(config+12u); /* Native fresh load 327d2c. */
    uint32_t id=live+2u;
    *(volatile uint32_t *)(root+192u)=(uint32_t)root;
    *(volatile uint8_t *)(root+216u)=(uint8_t)id; /* BRHS delay slot. */
    if(mode<5u && mode!=3u) {
        *(volatile uint32_t *)(half+44u)=
            (uint32_t)(uintptr_t)opencfw_em9305_init_transition_callback_32805c;
        *(volatile uint32_t *)(half+40u)=
            (uint32_t)(uintptr_t)opencfw_em9305_init_transition_callback_328018;
        *(volatile uint32_t *)(half+28u)=0x805408u;
    } else {
        *(volatile uint32_t *)(half+28u)=0u;
    }
    if((mode|2u)==2u) {
        uintptr_t row=config+61u;
        uint8_t count=*(volatile uint8_t *)(row+31u);
        frame[0]=4u;
        frame[4]=(uint8_t)(count+6u);
        uint32_t encoded=opencfw_em9305_radio_encode_3239d4(
            0x8053d0u,(uintptr_t)frame);
        uint32_t processed=opencfw_em9305_init_transition_segment_3243dc(
            encoded*2u,value16,value20,row);
        *(volatile uint8_t *)(row+32u)=0u;
        *(volatile uint32_t *)(uintptr_t)0x80539cu=encoded;
        *(volatile uint8_t *)(uintptr_t)0x8053adu=(uint8_t)(processed+encoded);
    } else {
        *(volatile uint32_t *)(half+32u)=0u;
    }
    *(volatile uint16_t *)(root+40u)=0u;
    (void)opencfw_em9305_associated_object_init_312918(active,0u);
    return opencfw_em9305_auxiliary_insert_313220(active);
}

#ifdef __arc__
__asm__(
".text\n.balign 4\n.global opencfw_em9305_init_transition_start_327b60\n"
".type opencfw_em9305_init_transition_start_327b60,@function\n"
"opencfw_em9305_init_transition_start_327b60:\n"
"enter_s [r13-r22,fp,blink]\nsub_s sp,sp,0x18\n"
"mov r0,sp\nbl opencfw_em9305_init_transition_start_327b60_body\n"
"leave_s [r13-r22,fp,blink,pcl]\n"
".size opencfw_em9305_init_transition_start_327b60,. - opencfw_em9305_init_transition_start_327b60\n");
#else
uint32_t opencfw_em9305_init_transition_start_327b60(void)
{
    uint8_t frame[24] __attribute__((aligned(4)));
    return opencfw_em9305_init_transition_start_327b60_body(frame);
}
#endif
