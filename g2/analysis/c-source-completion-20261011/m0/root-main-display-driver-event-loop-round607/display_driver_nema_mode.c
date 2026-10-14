/* Apollo NEMA mode 0x513924..0x513e0b, instruction-derived C candidate. */
#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[1];
extern const uint32_t display_driver_nema_mode_format_a[12];
extern const uint32_t display_driver_nema_mode_format_b[12];
extern const uint32_t display_driver_nema_mode_format_b_tail[4];
extern const uint32_t display_driver_nema_mode_target_bits[4];
extern void display_driver_nema_select_522a16(uint32_t);
extern void display_driver_gpu_mode_mask_4b1588(uint32_t);
extern void audio_uart_nema_rop_blend_mode_522956(uint32_t);
extern void display_driver_nema_mode_control_5226d6(uint32_t);
extern void audio_uart_nema_instruction_upload_522920(const uint32_t *,uint32_t,uint32_t);
extern void display_driver_nema_mode_commit_52294c(uint32_t);
struct nema_boot_state {
    volatile uint8_t mode_flag;
    volatile uint8_t override_flag;
    uint8_t reserved[2];
    volatile uint32_t word;
};
extern struct nema_boot_state audio_uart_nema_boot_state_200043a8;

static uint32_t format_a(uint32_t index) {
    return index<12u?display_driver_nema_mode_format_a[index]:
           display_driver_nema_mode_format_b[index-12u];
}
static uint32_t format_b(uint32_t index) {
    return index<12u?display_driver_nema_mode_format_b[index]:
           display_driver_nema_mode_format_b_tail[index-12u];
}
static void append(uint32_t *words,uint32_t *count,uint32_t first,uint32_t second) {
    words[*count*2u]=first;
    words[*count*2u+1u]=second;
    ++*count;
}
void display_driver_nema_mode_513924(uint32_t mode,uint32_t target,
                                    uint32_t surface,uint32_t alternate) {
    struct nema_boot_state *boot=&audio_uart_nema_boot_state_200043a8;
    volatile uint8_t *context=(volatile uint8_t *)(uintptr_t)audio_uart_nema_context_cell[0];
    if(boot->override_flag!=0u) {
        display_driver_nema_select_522a16(0x20202020u);
        surface=UINT32_MAX;
        alternate=UINT32_MAX;
        mode=0x101u;
        display_driver_gpu_mode_mask_4b1588(0u);
    }
    uint32_t bit23=(mode>>23)&1u,bit22=(mode>>22)&1u;
    uint32_t sign=(mode>>31)&1u,bit21=(mode>>21)&1u;
    uint32_t upper=mode&0xfff00000u,bit20=(mode>>20)&1u;
    uint32_t low=mode&15u,high=(mode>>8)&15u,bit25=(mode>>25)&1u;
    if(target>3u)target=0u;
    if(surface>3u)surface=UINT32_MAX;
    uint32_t selected=alternate;
    if(selected>3u)selected=target;
    if(boot->mode_flag!=0u) {
        uint32_t moved=0u;
        if(sign!=0u){moved=0x80000000u;sign=0u;mode&=0x7fffffffu;}
        if(bit25!=0u){moved|=0x02000000u;bit25=0u;mode&=0xfdffffffu;}
        if((mode&0x01000000u)!=0u||selected!=target) {
            audio_uart_nema_rop_blend_mode_522956(moved|1u);
            bit20=0u;
        } else {
            audio_uart_nema_rop_blend_mode_522956(moved|low|(high<<8));
            high=0u;low=1u;mode=(mode&0xfff00000u)|1u;
        }
    }
    uint32_t effect=bit25|sign;
    uint32_t current=0u;
    if(mode==1u)current=context[10];
    if(mode==1u&&current==0u&&target==0u) {
        uint32_t value;
        if((int32_t)surface<0) {
            display_driver_nema_mode_control_5226d6(1u);
            value=(boot->word<<16)|0x141f001fu;
        } else {
            display_driver_nema_mode_control_5226d6(0u);
            value=display_driver_nema_mode_target_bits[surface]|
                  (boot->word<<16)|0x141f801fu;
        }
        display_driver_nema_mode_commit_52294c(value);
        return;
    }
    uint32_t bit30=(mode>>30)&1u,bit29=(mode>>29)&1u;
    uint32_t bit27=(mode>>27)&1u,bit26=(mode>>26)&1u;
    uint32_t bit28=(mode>>28)&1u;
    uint32_t mode_bytes=bit26|(bit29<<8)|((alternate&0xffu)<<16)|(bit22<<24);
    uint32_t special=low<6u&&effect==0u&&high==0u?0u:3u;
    uint32_t special_flag=special!=0u;
    uint32_t blend=bit30;
    uint32_t instruction_kind=bit28!=0u?1u:3u;
    uint32_t effect_code=bit25!=0u?0x100000u:(effect<<21);
    uint32_t format=bit20!=0u?0x17u:(bit29!=0u?0x11u:(bit26!=0u?4u:0x1du));
    uint32_t precision=(bit28==0u&&bit27==0u)?0xeu:0xcu;
    uint32_t words[32];uint32_t count=0u;
    uint32_t final_or=0u;uint32_t control=1u;
    if(context[10]==0u) {
        if((int32_t)surface<0) {
            if(special_flag!=0u) {
                special_flag=0u;special=0u;
                final_or=display_driver_nema_mode_target_bits[selected]|0xb000u;
            }
        } else {
            control=0u;
            final_or=display_driver_nema_mode_target_bits[surface]|0x8000u;
        }
        uint32_t extra=(bit23!=0u||bit22!=0u);
        if(bit23!=0u)final_or=0xcc00u;
        else if(bit22!=0u)final_or=0xdc00u;
        if(bit21==0u||surface==UINT32_MAX) {
            if(extra!=0u)append(words,&count,(surface<<7)|0xc100bu,0x2000u);
        } else {
            append(words,&count,(surface<<7)|0x80c100bu,0x2000u);
            append(words,&count,(((mode_bytes>>16)&0xffu)<<7)|0x100bu,0u);
        }
        if(extra!=0u)append(words,&count,0xc0000u,0x81a042u);
    } else {
        append(words,&count,0xf40182u,0x2009408u);
        final_or=0xfc00u;
        if((int32_t)surface>=0) {
            append(words,&count,(surface<<7)|0xc100bu,0x2000u);
            control=0u;
        }
    }
    if(high<2u&&upper==0u&&(int32_t)surface<0&&selected==target) {
        uint32_t flag_a=high==0u?0x2000u:0x800u;
        uint32_t flag_b=high==0u?0x800000u:0x200000u;
        append(words,&count,(target<<7)|0x80c0002u,
               flag_a|(format_a(low)<<14)|(format_b(low)<<5)|flag_b|0x8a000006u);
    } else if(low<6u&&bit20==0u&&bit29==0u&&bit26==0u&&bit27==0u&&bit28==0u) {
        if((high!=0u||effect!=0u)&&special_flag==0u&&bit30==0u&&low<2u) {
            uint32_t flag_a=low==0u?0x2000u:0u;
            uint32_t flag_b=low==0u?0x800000u:0u;
            append(words,&count,effect_code|(target<<7)|0x4e0002u,
                   flag_b|flag_a|(format_a(high)<<14)|(format_b(high)<<5)|
                   0x80080206u);
            goto finalize;
        }
        uint32_t base=special|0x80c0000u;
        uint32_t first=blend<<20;
        uint32_t flag_a=0x1000u,flag_b=0x400000u;
        uint32_t use_effect=effect;
        if(high==0u)blend=effect;
        if(high!=0u||blend!=0u) {
            uint32_t extra=selected;
            if(special_flag==0u&&bit30==0u) {
                if(low==0u){flag_a=0x2000u;flag_b=0x800000u;}
                else if(low==1u){flag_a=0u;flag_b=0u;}
            }
            append(words,&count,first|base|((extra&0xffu)<<7),
                   (format_a(low)<<14)|(format_b(low)<<5)|0xa002007u);
        } else {
            base=0x80c0002u;
            use_effect=0x80000000u;
            append(words,&count,first|base|((target&0xffu)<<7),
                   use_effect|(format_a(low)<<14)|(format_b(low)<<5)|0xa002007u);
            goto finalize;
        }
        append(words,&count,effect_code|(target<<7)|0x4e0002u,
               flag_b|flag_a|(format_a(high)<<14)|(format_b(high)<<5)|0x80080206u);
    } else {
        uint32_t op=bit20!=0u?7u:4u;
        uint32_t active=(high|special)!=0u?(high|special):effect;
        if(active==0u&&low==1u&&blend==0u) {
            append(words,&count,(target<<7)|0x80c0002u,
                   instruction_kind|(precision<<5)|(format<<14)|(op<<11)|
                   0x80000004u);
        } else if(active!=0u||format!=0x1du||precision!=0xeu||blend!=0u||special!=0u) {
            append(words,&count,special|(selected<<7)|(blend<<20)|0x80c0000u,
                   instruction_kind|(precision<<5)|(format<<14)|(op<<11)|4u);
        } else {
            append(words,&count,(blend<<20)|(target<<7)|0x80c0002u,
                   instruction_kind|(precision<<5)|(format<<14)|(op<<11)|4u);
        }
        if(!(active==0u&&low==1u&&blend==0u)) {
            if(high==0u&&effect==0u) {
                append(words,&count,(target<<7)|0x80c0002u,
                       0x80000000u|(format_a(low)<<14)|(format_b(low)<<5)|
                       0xa002007u);
            } else {
                uint32_t flag_a=0x1000u,flag_b=0x400000u;
                if(special_flag==0u&&bit30==0u) {
                    if(low==0u){flag_a=0x2000u;flag_b=0x800000u;}
                    else if(low==1u){flag_a=0u;flag_b=0u;}
                }
                append(words,&count,effect_code|(target<<7)|0x4e0002u,
                       flag_b|flag_a|(format_a(high)<<14)|(format_b(high)<<5)|
                       0x80080206u);
            }
        }
    }
finalize:
    display_driver_nema_mode_control_5226d6(control);
    audio_uart_nema_instruction_upload_522920(words,count,0u);
    display_driver_nema_mode_commit_52294c(final_or|
        ((0x20u-count)|boot->word|display_driver_nema_mode_target_bits[selected])<<16|
        0x10000000u);
}
