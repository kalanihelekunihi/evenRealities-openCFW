/* SPDX-License-Identifier: MIT */
/* Clean-room hardware-state nibble composer and dual-output classifier. */
typedef __UINT8_TYPE__ open_cfw_hw_decode_u8;
typedef __UINT32_TYPE__ open_cfw_hw_decode_u32;

#if defined(__arm__) || defined(__thumb__)
__attribute__((used,noinline,naked,visibility("default")))
open_cfw_hw_decode_u32 open_cfw_bootloader_hw_state_decode_42b6b8(
    const void *input,open_cfw_hw_decode_u32 *primary,
    open_cfw_hw_decode_u32 *secondary)
{
    __asm volatile(
        "push {r4,r5}\nldr.w r3,[pc,#0x8ec]\nldr r4,[r3]\n"
        "ldrb r3,[r0,#0x10]\nands r3,r3,#0xf\nbfi r4,r3,#8,#4\n"
        "ldrb r3,[r0,#0x11]\ncmp r3,#1\nbne low_not_one\nmovs r3,#1\n"
        "bfi r4,r3,#0,#4\nb low_done\nlow_not_one:\nldrb r3,[r0,#0x11]\n"
        "cmp r3,#0\nbne low_dynamic\nlsrs r4,r4,#4\nlsls r4,r4,#4\n"
        "b low_done\nlow_dynamic:\nldr.w r3,[pc,#0x8c4]\nldr r3,[r3]\n"
        "ands r3,r3,#3\ncmp r3,#2\nbeq low_dynamic_one\nlsrs r4,r4,#4\n"
        "lsls r4,r4,#4\nb low_done\nlow_dynamic_one:\nmovs r3,#1\n"
        "bfi r4,r3,#0,#4\nlow_done:\nldrb r3,[r0,#0x12]\ncmp r3,#1\n"
        "beq flag4_one\nldrb r3,[r0,#0x12]\ncmp r3,#2\nbeq flag4_one\n"
        "ldr r3,[r0]\nlsls r3,r3,#2\nbne flag4_one\nldr r3,[r0,#4]\n"
        "movw r5,#0x4c4\ntst r3,r5\nbeq flag4_zero\nflag4_one:\nmovs r3,#1\n"
        "bfi r4,r3,#4,#4\nb flag4_done\nflag4_zero:\nbics r4,r4,#0xf0\n"
        "flag4_done:\nldrb r3,[r0,#0x12]\ncmp r3,#2\nbne field12_not_two\n"
        "movs r3,#2\nbfi r4,r3,#0xc,#4\nb field12_done\n"
        "field12_not_two:\nldrb r3,[r0,#0x12]\ncmp r3,#1\nbne field12_zero\n"
        "movs r3,#1\nbfi r4,r3,#0xc,#4\nb field12_done\n"
        "field12_zero:\nbics r4,r4,#0xf000\nfield12_done:\nldr r3,[r0]\n"
        "lsls r3,r3,#2\nbne flag16_one\nldr r3,[r0,#4]\nmovw r5,#0x4c4\n"
        "tst r3,r5\nbeq flag16_zero\nflag16_one:\nmovs r3,#1\n"
        "bfi r4,r3,#0x10,#4\nb flag16_done\nflag16_zero:\nbics r4,r4,#0xf0000\n"
        "flag16_done:\nldr r0,[r0]\ntst.w r0,#0xc00000\nbeq flag20_zero\n"
        "movs r0,#1\nbfi r4,r0,#0x14,#4\nb flag20_done\n"
        "flag20_zero:\nbics r4,r4,#0xf00000\nflag20_done:\n"
        "ldr.w r0,[pc,#0x838]\nands r0,r4\ncmp r0,#0\nbeq.w primary_0\n"
        "subs r0,r0,#1\nbeq.w primary_1\nsubs r0,#0xf\nbeq.w primary_16\n"
        "subs r0,r0,#1\nbeq.w primary_17\nsubs r0,#0xef\nbeq.w primary_256\n"
        "subs r0,r0,#1\nbeq.w primary_257\nsubs r0,#0xf\nbeq.w primary_272\n"
        "subs r0,r0,#1\nbeq.w primary_273\nsubs r0,#0xef\nbeq primary_512\n"
        "subs r0,r0,#1\nbeq.w primary_513\nsubs r0,#0xf\nbeq.w primary_528\n"
        "subs r0,r0,#1\nbeq.w primary_529\nsubs r0,#0xef\nbeq primary_768\n"
        "subs r0,r0,#1\nbeq.w primary_769\nsubs r0,#0xf\nbeq.w primary_784\n"
        "subs r0,r0,#1\nbeq.w primary_785\nldr.w r3,[pc,#0x7d8]\nsubs r0,r0,r3\n"
        "beq.w primary_100010\nsubs r0,r0,#1\nbeq.w primary_17\n"
        "subs r0,#0xff\nbeq.w primary_100110\nsubs r0,r0,#1\n"
        "beq.w primary_273\nsubs r0,#0xff\nbeq.w primary_100210\n"
        "subs r0,r0,#1\nbeq.w primary_529\nsubs r0,#0xff\n"
        "beq.w primary_100310\nsubs r0,r0,#1\nbeq.w primary_785\n"
        "b invalid\nprimary_768:\nldr.w r0,[pc,#0x7a8]\nldrb r0,[r0]\n"
        "lsls r0,r0,#0x1f\nbpl primary_768_base\nmovs r0,#4\nstr r0,[r1]\n"
        "b primary_done\nprimary_768_base:\nmovs r0,#0\nstr r0,[r1]\n"
        "primary_done:\nldr.w r0,[pc,#0x798]\nands r4,r0\ncmp r4,#0\n"
        "beq secondary_0\ncmp r4,#1\nbeq.w secondary_1\n"
        "cmp.w r4,#0x1000\nbeq.w secondary_2\nmovw r0,#0x1001\ncmp r4,r0\n"
        "beq.w secondary_4\ncmp.w r4,#0x2000\nbeq.w secondary_3\n"
        "movw r0,#0x2001\ncmp r4,r0\nbeq.w secondary_5\n"
        "cmp.w r4,#0x10000\nbeq.w secondary_6\ncmp.w r4,#0x10001\n"
        "beq.w secondary_7\ncmp.w r4,#0x11000\nbeq.w secondary_2\n"
        "ldr.w r0,[pc,#0x750]\ncmp r4,r0\nbeq.w secondary_4\n"
        "cmp.w r4,#0x12000\nbeq.w secondary_3\nldr.w r0,[pc,#0x740]\n"
        "cmp r4,r0\nbeq.w secondary_5\nb invalid_secondary\nsecondary_0:\n"
        "movs r0,#0\nstr r0,[r2]\nreturn_ok:\nmovs r0,#0\nreturn_status:\npop {r4,r5}\n"
        "bx lr\nprimary_512:\nldr.w r0,[pc,#0x720]\nldrb r0,[r0]\n"
        "lsls r0,r0,#0x1f\nbpl primary_512_base\nmovs r0,#5\nstr r0,[r1]\n"
        "b primary_512_done\nprimary_512_base:\nmovs r0,#1\nstr r0,[r1]\n"
        "primary_512_done:\nb primary_done\nprimary_256:\nldr.w r0,[pc,#0x708]\nldrb r0,[r0]\n"
        "lsls r0,r0,#0x1f\nbpl primary_256_base\nmovs r0,#6\nstr r0,[r1]\n"
        "b primary_256_done\nprimary_256_base:\nmovs r0,#2\nstr r0,[r1]\n"
        "primary_256_done:\nb primary_done\nprimary_0:\nldr.w r0,[pc,#0x6f4]\nldrb r0,[r0]\n"
        "lsls r0,r0,#0x1f\nbpl primary_0_base\nmovs r0,#7\nstr r0,[r1]\n"
        "b primary_0_done\nprimary_0_base:\nmovs r0,#3\nstr r0,[r1]\n"
        "primary_0_done:\nb primary_done\nprimary_784:\nmovs r0,#4\nstr r0,[r1]\nb primary_done\n"
        "primary_528:\nmovs r0,#5\nstr r0,[r1]\nb primary_done\n"
        "primary_272:\nmovs r0,#6\nstr r0,[r1]\nb primary_done\n"
        "primary_16:\nmovs r0,#7\nstr r0,[r1]\nb primary_done\n"
        "primary_769:\nldr.w r0,[pc,#0x6c4]\nldrb r0,[r0]\nlsls r0,r0,#0x1f\n"
        "bpl primary_769_base\nmovs r0,#0xc\nstr r0,[r1]\nb primary_769_done\n"
        "primary_769_base:\nmovs r0,#8\nstr r0,[r1]\nprimary_769_done:\nb primary_done\n"
        "primary_513:\nldr.w r0,[pc,#0x6b0]\nldrb r0,[r0]\nlsls r0,r0,#0x1f\n"
        "bpl primary_513_base\nmovs r0,#0xd\nstr r0,[r1]\nb primary_513_done\n"
        "primary_513_base:\nmovs r0,#9\nstr r0,[r1]\nprimary_513_done:\nb primary_done\n"
        "primary_257:\nldr.w r0,[pc,#0x698]\nldrb r0,[r0]\nlsls r0,r0,#0x1f\n"
        "bpl primary_257_base\nmovs r0,#0xe\nstr r0,[r1]\nb primary_257_done\n"
        "primary_257_base:\nmovs r0,#0xa\nstr r0,[r1]\nprimary_257_done:\nb primary_done\n"
        "primary_1:\nldr.w r0,[pc,#0x684]\nldrb r0,[r0]\nlsls r0,r0,#0x1f\n"
        "bpl primary_1_base\nmovs r0,#0xf\nstr r0,[r1]\nb primary_1_done\n"
        "primary_1_base:\nmovs r0,#0xb\nstr r0,[r1]\nprimary_1_done:\nb primary_done\n"
        "primary_785:\nmovs r0,#0xc\nstr r0,[r1]\nb primary_done\n"
        "primary_529:\nmovs r0,#0xd\nstr r0,[r1]\nb primary_done\n"
        "primary_273:\nmovs r0,#0xe\nstr r0,[r1]\nb primary_done\n"
        "primary_17:\nmovs r0,#0xf\nstr r0,[r1]\nb primary_done\n"
        "primary_100310:\nmovs r0,#0x10\nstr r0,[r1]\nb primary_done\n"
        "primary_100210:\nmovs r0,#0x11\nstr r0,[r1]\nb primary_done\n"
        "primary_100110:\nmovs r0,#0x12\nstr r0,[r1]\nb primary_done\n"
        "primary_100010:\nmovs r0,#0x13\nstr r0,[r1]\nb primary_done\n"
        "invalid:\nmovs r0,#5\nb return_status\nsecondary_1:\n"
        "ldr.w r0,[pc,#0x638]\nldrb r0,[r0]\nlsls r0,r0,#0x1f\n"
        "bpl secondary_1_base\nmovs r0,#7\nstr r0,[r2]\nb secondary_1_done\n"
        "secondary_1_base:\nmovs r0,#1\nstr r0,[r2]\nsecondary_1_done:\nb return_ok\n"
        "secondary_2:\nmovs r0,#2\nstr r0,[r2]\nb return_ok\n"
        "secondary_3:\nmovs r0,#3\nstr r0,[r2]\nb return_ok\n"
        "secondary_4:\nmovs r0,#4\nstr r0,[r2]\nb return_ok\n"
        "secondary_5:\nmovs r0,#5\nstr r0,[r2]\nb return_ok\n"
        "secondary_6:\nmovs r0,#6\nstr r0,[r2]\nb return_ok\n"
        "secondary_7:\nmovs r0,#7\nstr r0,[r2]\nb return_ok\n"
        "invalid_secondary:\nmovs r0,#5\nb return_status\n");
}
#else
typedef struct {open_cfw_hw_decode_u32 word0,word4;open_cfw_hw_decode_u8 pad[8];
    open_cfw_hw_decode_u8 field8,mode,kind;} open_cfw_hw_decode_input;
static open_cfw_hw_decode_u32 open_cfw_hw_decode_primary(open_cfw_hw_decode_u32 v,
    open_cfw_hw_decode_u32 alternate,open_cfw_hw_decode_u32 *out)
{
    switch(v){
    case 0:*out=alternate?7:3;break;case 1:*out=alternate?15:11;break;
    case 16:*out=7;break;case 17:*out=15;break;case 256:*out=alternate?6:2;break;
    case 257:*out=alternate?14:10;break;case 272:*out=6;break;case 273:*out=14;break;
    case 512:*out=alternate?5:1;break;case 513:*out=alternate?13:9;break;
    case 528:*out=5;break;case 529:*out=13;break;case 768:*out=alternate?4:0;break;
    case 769:*out=alternate?12:8;break;case 784:*out=4;break;case 785:*out=12;break;
    case 0x100010:*out=19;break;case 0x100011:*out=15;break;
    case 0x100110:*out=18;break;case 0x100111:*out=14;break;
    case 0x100210:*out=17;break;case 0x100211:*out=13;break;
    case 0x100310:*out=16;break;case 0x100311:*out=12;break;
    default:return 5U;}return 0U;
}
static open_cfw_hw_decode_u32 open_cfw_hw_decode_secondary(open_cfw_hw_decode_u32 v,
    open_cfw_hw_decode_u32 alternate,open_cfw_hw_decode_u32 *out)
{
    switch(v){case 0:*out=0;break;case 1:*out=alternate?7:1;break;
    case 0x1000:case 0x11000:*out=2;break;case 0x2000:case 0x12000:*out=3;break;
    case 0x1001:case 0x11001:*out=4;break;case 0x2001:case 0x12001:*out=5;break;
    case 0x10000:*out=6;break;case 0x10001:*out=7;break;default:return 5U;}
    return 0U;
}
__attribute__((used,noinline,visibility("default")))
open_cfw_hw_decode_u32 open_cfw_bootloader_hw_state_decode_42b6b8_portable(
    const open_cfw_hw_decode_input *in,open_cfw_hw_decode_u32 initial,
    open_cfw_hw_decode_u32 dynamic_mode,open_cfw_hw_decode_u32 alternate,
    open_cfw_hw_decode_u32 *primary,open_cfw_hw_decode_u32 *secondary)
{
    open_cfw_hw_decode_u32 state=initial,active;
    if(in==0U||primary==0U||secondary==0U)return ~0U;
    state=(state&~0xF00U)|(((open_cfw_hw_decode_u32)in->field8&15U)<<8U);
    active=in->mode==1U||(in->mode!=0U&&(dynamic_mode&3U)==2U);
    state=(state&~15U)|(active?1U:0U);
    active=in->kind==1U||in->kind==2U||(in->word0<<2U)!=0U||
        (in->word4&0x4C4U)!=0U;state=(state&~0xF0U)|(active?0x10U:0U);
    state=(state&~0xF000U)|((in->kind==2U?2U:in->kind==1U?1U:0U)<<12U);
    active=(in->word0<<2U)!=0U||(in->word4&0x4C4U)!=0U;
    state=(state&~0xF0000U)|(active?0x10000U:0U);
    state=(state&~0xF00000U)|((in->word0&0xC00000U)!=0U?0x100000U:0U);
    if(open_cfw_hw_decode_primary(state&0xF00FFFU,alternate,primary)!=0U)return 5U;
    return open_cfw_hw_decode_secondary(state&0x0FF00FU,alternate,secondary);
}
#endif
