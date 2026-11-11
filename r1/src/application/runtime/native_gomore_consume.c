#include <stdint.h>
#include <stddef.h>

extern void __aeabi_memclr(void *,size_t);
extern void r1_gomore_table_record11_native(volatile void *,uint32_t);
extern int32_t r1_gomore_packed_timeline_extract_native(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern void r1_gomore_sleep_stage_refine_native(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,volatile int32_t *);
extern void r1_gomore_prepare_score_native(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,volatile void *,volatile float *);
extern void r1_gomore_shift_marked_history_native(volatile void *,int32_t);
struct __attribute__((packed,may_alias)) consume_word { uint32_t value; };
static uint32_t word(const volatile void *p)
{ return ((const volatile struct consume_word *)p)->value; }
static void store(volatile void *p,uint32_t value)
{ ((volatile struct consume_word *)p)->value=value; }
static uint32_t bits(float value)
{ union {float f;uint32_t u;} v={.f=value};return v.u; }
static float from_bits(uint32_t value)
{ union {float f;uint32_t u;} v={.u=value};return v.f; }
/* The signaling compare with zero updates FPSCR without performing a C
 * floating-point comparison that would quiet a qNaN differently. */
static uint32_t signaling_zero_flags(float x)
{
    uint32_t raw=bits(x),fp=__builtin_arm_get_fpscr();
    uint32_t magnitude=raw&UINT32_C(0x7fffffff),flags;
    if ((fp&(1u<<24)) && magnitude && magnitude<UINT32_C(0x00800000)) {
        raw&=UINT32_C(0x80000000);
        magnitude=0;
        fp|=UINT32_C(0x80);
    }
    if (magnitude>UINT32_C(0x7f800000)) {
        flags=UINT32_C(0x30000000);
        fp|=1u;
    } else if (!magnitude) {
        flags=UINT32_C(0x60000000);
    } else {
        flags=(raw>>31)?UINT32_C(0x80000000):UINT32_C(0x20000000);
    }
    uint32_t result=(fp&UINT32_C(0x0fffffff))|flags;
    __builtin_arm_set_fpscr(result);
    return result;
}
__attribute__((noinline)) static float half_gain(float x)
{ return x*0.5f; }

uint32_t r1_gomore_recent_interval_native(const volatile void *input,uint32_t now)
{
    const volatile uint8_t *p=input;
    if (!(p[26]&8u)) return 0;
    uint32_t start=word(p),end=word(p+4);
    if (end<=start) return 0;
    uint32_t duration=end-start;
    if (duration>86400u || duration<900u) return 0;
    if (start+86400u<=now || end>now) return 0;
    return 1;
}

/* frame is the native 116-byte local area below seven saved words.
 * The table11 high byte at frame+31 deliberately retains incoming stack data. */
__attribute__((noinline,used)) uint32_t
r1_gomore_packed_sleep_consume_body(uint32_t context,uint32_t state,
        volatile void *input,volatile uint32_t *unused_count,
        volatile void *output,volatile uint8_t *frame)
{
    (void)unused_count;
    volatile uint8_t *work=output;
    volatile uint8_t *record=input;
    uint32_t payload=word(work+8);
    __aeabi_memclr((void *)work,88);
    store(work+8,payload);
    uint32_t now=word((const volatile void *)(uintptr_t)(context+720u));
    if (!r1_gomore_recent_interval_native(record,now)) return UINT32_MAX;
    uint32_t kind=(record[26]&16u) ? 1u : 2u;
    work[84]=(uint8_t)kind;
    store(work,word(record));store(work+4,word(record+4));
    if (kind!=1) return 0;
    __aeabi_memclr((void *)(frame+40),76);
    store(frame+36,0);store(frame+32,0);
    uint32_t index=*(const volatile uint8_t *)(uintptr_t)(context+8437u);
    r1_gomore_table_record11_native(frame+20,index);
    uint32_t r12=word(record+12),r16=word(record+16);
    uint32_t r20=word(record+20),data=word(work+8);
    uint32_t shift=(uint32_t)frame[21]*30u;
    uint32_t end=word(work+4)+shift,start=word(work)+shift;
    uint32_t r8=word(record+8);
    int32_t length=r1_gomore_packed_timeline_extract_native(
        context,start,end,r8,r12,r16,r20,data);
    store(frame+36,(uint32_t)length);
    volatile int32_t *live_length=(volatile int32_t *)(frame+36);
    volatile float *score=(volatile float *)(frame+32);
    if (length>0) {
        uint32_t interval=word(work+4)-word(work);
        r1_gomore_sleep_stage_refine_native(word(frame+20),word(frame+24),word(frame+28),
            word(work+8),0,interval,live_length);
        uint32_t mode=*(const volatile uint8_t *)(uintptr_t)(state+8u);
        interval=word(work+4)-word(work);
        r1_gomore_prepare_score_native(word(work+8),0,interval,0,mode,frame+40,score);
        store(work+16,word(frame+36));
    }
    float gain=from_bits(word(frame+44));
    uint32_t comparison=signaling_zero_flags(gain);
    if ((comparison&UINT32_C(0xf0000000))==UINT32_C(0x20000000)) {
        float half=half_gain(gain);
        uint32_t half_bits=bits(half);
        uint32_t lower=(int32_t)half_bits<INT32_C(0x3f000000) ? UINT32_C(0x3f000000) : half_bits;
        uint32_t bounded=(int32_t)lower>=INT32_C(0x41200000) ? UINT32_C(0x41200000) :
            ((int32_t)half_bits<INT32_C(0x3f000000) ? UINT32_C(0x3f000000) : half_bits);
        int32_t scaled=(int32_t)(from_bits(bounded)*2.0f);
        int32_t adjustment=(int8_t)scaled;
        store(work,word(work)-(uint32_t)(adjustment*30));
        r1_gomore_shift_marked_history_native(work,adjustment);
        uint32_t mode=*(const volatile uint8_t *)(uintptr_t)(state+8u);
        uint32_t interval=word(work+4)-word(work);
        r1_gomore_prepare_score_native(word(work+8),0,interval,0,mode,frame+40,score);
    }
    store(work+80,word(frame+32));
    float m10=from_bits(word(frame+80));store(work+60,bits(m10));
    float m8=from_bits(word(frame+72));store(work+52,bits(m8));
    float m9=from_bits(word(frame+76));store(work+56,bits(m9));
    float remaining=1.0f-m10;remaining=remaining-m8;remaining=remaining-m9;
    store(work+48,bits(remaining));
    store(work+76,word(frame+112));store(work+72,word(frame+108));
    store(work+64,word(frame+100));store(work+68,word(frame+104));
    store(work+28,word(frame+48));store(work+32,word(frame+56));
    store(work+36,word(frame+60));store(work+40,word(frame+64));store(work+44,word(frame+40));
    return 0;
}

/* Under the pinned Arm Clang profile, the 128-byte alloca and two saved
 * registers place the outgoing call area at entry SP-144. The worker's
 * source-level frame starts at that call area; bytes 0..7 hold its two stack
 * arguments, and its used bytes 20..115 are inside the allocated area.
 * This retains the stock table record's raw byte at frame+31 without writing
 * an invented padding value. The paired Cortex-M replay checks the frame
 * address and provider SP, so a changed compiler layout fails that gate. */
__attribute__((noinline)) uint32_t r1_gomore_packed_sleep_consume_native(
        uint32_t context,uint32_t state,volatile void *input,
        volatile uint32_t *count,volatile void *output)
{
    volatile uint8_t *frame=(volatile uint8_t *)
        ((uintptr_t)__builtin_alloca(128u)-8u);
    return r1_gomore_packed_sleep_consume_body(
        context,state,input,count,output,frame);
}
