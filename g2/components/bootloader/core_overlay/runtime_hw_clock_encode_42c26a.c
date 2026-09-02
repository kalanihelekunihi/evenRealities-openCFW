/* SPDX-License-Identifier: MIT */
/* Clean-room hardware clock-divider search and register-field encoder. */
typedef __UINT8_TYPE__ open_cfw_hw_clock_u8;
typedef __UINT32_TYPE__ open_cfw_hw_clock_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_rounded_divider_42c222(void);
extern void open_cfw_bootloader_is_power_of_two_42c256(void);

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_hw_clock_encode_42c26a(void)
{__asm volatile(
 "push.w {r2,r3,r4,r5,r6,r7,r8,lr}\ncmp r0,#0\nbne input_ok\n"
 "movs r0,#0\nmovs r1,#0\nb finish\n"
 "input_ok: ldr.w r6,[pc,#0x704]\nudiv r2,r6,r0\nmls r2,r0,r2,r6\n"
 "cmp r2,#0\nbeq exact_divide\nmovs r3,#1\nb add_quotient\n"
 "exact_divide: movs r3,#0\n"
 "add_quotient: udiv r2,r6,r0\nadds r3,r3,r2\nrsbs r2,r3,#0\nands r2,r3\n"
 "clz r7,r2\nrsbs.w r7,r7,#0x1f\ncmp r7,#7\nblt exponent_capped\nmovs r7,#6\n"
 "exponent_capped: cmp.w r0,r6,lsr #14\nblo special_true\nmovs r2,#3\n"
 "udiv r2,r6,r2\ncmp r0,r2\nblo special_false\nmovs r2,r6\nlsrs r2,r2,#1\n"
 "subs r2,r2,#1\ncmp r2,r0\nblo special_false\n"
 "special_true: movs r5,#1\nb special_done\n"
 "special_false: movs r5,#0\n"
 "special_done: movs r4,#1\nlsls.w ip,r4,r7\nlsls r2,r5,#1\nadds r2,r2,#1\n"
 "mul r2,r2,ip\nudiv ip,r3,r2\nmov lr,r3\nudiv r8,lr,r2\n"
 "mls r2,r2,r8,lr\ncmp r2,#0\nbeq rounded_done\nadds.w ip,ip,#1\nb rounded_done\n"
 "rounded_done: clz lr,ip\nrsbs.w lr,lr,#0x1f\ncmp.w lr,#8\nblo scaled_done\n"
 "adds.w r7,r7,lr\nsubs r7,r7,#7\nb scaled_done\n"
 "scaled_done: adds r7,r7,#1\ncmp r7,#8\nblo exponent_ok\nmovs r0,#0\nmovs r1,#0\nb finish\n"
 "exponent_ok: cmp.w lr,#8\nblo quotient_ready\nmov r2,ip\nadds.w r8,lr,#0xf9\n"
 "lsrs.w ip,ip,r8\nsubs.w lr,lr,#7\nlsls.w lr,r4,lr\nudiv r8,r2,lr\n"
 "mls r2,lr,r8,r2\ncmp r2,#0\nbeq quotient_ready\nadds.w ip,ip,#1\nb quotient_ready\n"
 "quotient_ready: cmp.w r0,r6,lsr #2\nbhs exact_power\nadds.w r0,r7,#0xff\n"
 "lsls r4,r0\ncmp r4,r3\nbne inexact_power\n"
 "exact_power: movs r3,#0\nb power_done\n"
 "inexact_power: movs r3,#1\n"
 "power_done: cmp r1,#1\nbne normal_phase\nsubs.w r4,ip,#2\nlsrs r4,r4,#1\nb phase_done\n"
 "normal_phase: subs.w r4,ip,#1\nlsrs r4,r4,#1\n"
 "phase_done: lsls r0,r7,#8\nands r0,r0,#0xf00\nlsls r1,r5,#0xc\n"
 "ands r1,r1,#0x1000\norrs r0,r1\nlsls r1,r3,#0xd\nands r1,r1,#0x2000\n"
 "orrs r0,r1\nlsls r4,r4,#0x10\nands r4,r4,#0xff0000\norrs r4,r0\n"
 "subs.w r0,ip,#1\norrs.w r4,r4,r0,lsl #24\nsubs.w ip,ip,#1\nstr.w ip,[sp]\n"
 "movs r2,r5\nmovs r1,r7\nmovs r0,r6\nbl open_cfw_bootloader_rounded_divider_42c222\n"
 "movs r5,r0\nldr.w r0,[pc,#0x5e8]\nudiv r1,r5,r0\nmls r0,r0,r1,r5\n"
 "cmp r0,#0\nbne return_value\nldr.w r0,[pc,#0x5d8]\nudiv r0,r5,r0\n"
 "bl open_cfw_bootloader_is_power_of_two_42c256\ncmp r0,#0\nbeq return_value\n"
 "movs r0,#0\nmovs r3,r0\nmovs r1,r0\nmovs r2,#1\nstr r0,[sp]\n"
 "movs r1,r7\nmovs r0,r6\nbl open_cfw_bootloader_rounded_divider_42c222\n"
 "movs r5,r0\nlsls r7,r7,#8\nands r7,r7,#0xf00\norrs r7,r7,#0x1000\nmovs r4,r7\n"
 "return_value: movs r1,r5\nmovs r0,r4\nfinish: pop.w {r2,r3,r4,r5,r6,r7,r8,pc}\n");}
#else
static open_cfw_hw_clock_u32 open_cfw_hw_clock_round(
    open_cfw_hw_clock_u32 numerator, open_cfw_hw_clock_u32 exponent,
    open_cfw_hw_clock_u32 multiplier_a, open_cfw_hw_clock_u32 multiplier_b,
    open_cfw_hw_clock_u32 multiplier_c)
{
    open_cfw_hw_clock_u32 denominator = ((multiplier_a*2U)+1U)
        *(1U<<(exponent-1U))*((multiplier_c*multiplier_b)+1U);
    return numerator/denominator+
        (numerator%denominator>(denominator>>1U)?1U:0U);
}

static open_cfw_hw_clock_u32 open_cfw_hw_clock_log2(
    open_cfw_hw_clock_u32 value)
{
    open_cfw_hw_clock_u32 result=0U;
    while(value>1U){value>>=1U;result++;}
    return result;
}

__attribute__((used,noinline,visibility("default")))
open_cfw_hw_clock_u32 open_cfw_bootloader_hw_clock_encode_42c26a_portable(
    open_cfw_hw_clock_u32 requested_hz, open_cfw_hw_clock_u32 phase_select,
    open_cfw_hw_clock_u32 *actual_hz)
{
    const open_cfw_hw_clock_u32 source_hz=96000000U;
    open_cfw_hw_clock_u32 ceiling,lowbit,exponent,special,scale,quotient;
    open_cfw_hw_clock_u32 quotient_log,exact_power,phase,encoding,actual;
    if(requested_hz==0U){if(actual_hz!=0)*actual_hz=0U;return 0U;}
    ceiling=(source_hz/requested_hz)+
        (source_hz%requested_hz!=0U?1U:0U);
    lowbit=(0U-ceiling)&ceiling;
    exponent=open_cfw_hw_clock_log2(lowbit);
    if(exponent>=7U)exponent=6U;
    special=(requested_hz<(source_hz>>14U) ||
             (requested_hz>=source_hz/3U &&
              requested_hz<=(source_hz/2U)-1U))?1U:0U;
    scale=(special*2U+1U)*(1U<<exponent);
    quotient=ceiling/scale+(ceiling%scale!=0U?1U:0U);
    quotient_log=open_cfw_hw_clock_log2(quotient);
    if(quotient_log>=8U)exponent+=quotient_log-7U;
    exponent++;
    if(exponent>=8U){if(actual_hz!=0)*actual_hz=0U;return 0U;}
    if(quotient_log>=8U){
        scale=1U<<(quotient_log-7U);
        quotient=quotient/scale+(quotient%scale!=0U?1U:0U);
    }
    exact_power=(requested_hz>=(source_hz>>2U) ||
                 (1U<<(exponent-1U))==ceiling)?0U:1U;
    phase=phase_select==1U?(quotient-2U)>>1U:(quotient-1U)>>1U;
    encoding=((exponent<<8U)&0xF00U)|((special<<12U)&0x1000U)|
        ((exact_power<<13U)&0x2000U)|((phase<<16U)&0xFF0000U)|
        ((quotient-1U)<<24U);
    actual=open_cfw_hw_clock_round(source_hz,exponent,special,exact_power,
                                   quotient-1U);
    if(actual%250000U==0U){
        open_cfw_hw_clock_u32 divided=actual/250000U;
        if(divided!=0U && (divided&(divided-1U))==0U){
            actual=open_cfw_hw_clock_round(source_hz,exponent,1U,0U,0U);
            encoding=((exponent<<8U)&0xF00U)|0x1000U;
        }
    }
    if(actual_hz!=0)*actual_hz=actual;
    return encoding;
}
#endif
