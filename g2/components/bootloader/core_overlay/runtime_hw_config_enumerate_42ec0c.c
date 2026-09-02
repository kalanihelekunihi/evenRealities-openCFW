/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room hardware configuration, channel normalization, and channel
 * enumeration services authenticated at 0x0042EC0C, 0x0042EE00, and
 * 0x0042EE70 in the G2 bootloader.
 */
typedef __UINT8_TYPE__ open_cfw_hwcfg_u8;
typedef __UINT32_TYPE__ open_cfw_hwcfg_u32;
#define OPEN_CFW_HWCFG_MAGIC 0x01AFAFAFU

#if defined(__arm__) || defined(__thumb__)

__attribute__((used, noinline, naked, visibility("default"), pcs("aapcs-vfp")))
open_cfw_hwcfg_u32 open_cfw_bootloader_hw_config_dispatch_42ec0c(
    open_cfw_hwcfg_u32 *handle, open_cfw_hwcfg_u32 operation, void *config)
{
    __asm volatile(
        "ldr r3, [r0, #4]\n"
        "cmp r0, #0\n"
        "beq .Lopen_cfw_hwcfg_invalid_handle\n"
        "ldr r0, [r0]\n"
        "bic r0, r0, #0xfe000000\n"
        "ldr.w r3, [pc, #1376]\n"
        "cmp r0, r3\n"
        "beq .Lopen_cfw_hwcfg_operation\n"
        ".Lopen_cfw_hwcfg_invalid_handle:\n"
        "movs r0, #2\n"
        "b .Lopen_cfw_hwcfg_return\n"
        ".Lopen_cfw_hwcfg_operation:\n"
        "uxtb r1, r1\n"
        "cmp r1, #0\n"
        "beq .Lopen_cfw_hwcfg_write_limits\n"
        "cmp r1, #2\n"
        "beq .Lopen_cfw_hwcfg_copy_full\n"
        "blo .Lopen_cfw_hwcfg_calculate\n"
        "cmp r1, #3\n"
        "beq .Lopen_cfw_hwcfg_copy_pair\n"
        "b .Lopen_cfw_hwcfg_bad_operation\n"
        ".Lopen_cfw_hwcfg_write_limits:\n"
        "ldr r0, [r2, #4]\n"
        "cmp.w r0, #0x100000\n"
        "bhs .Lopen_cfw_hwcfg_limit_error\n"
        "ldr r0, [r2, #8]\n"
        "cmp.w r0, #0x100000\n"
        "blo .Lopen_cfw_hwcfg_write_values\n"
        ".Lopen_cfw_hwcfg_limit_error:\n"
        "movs r0, #5\n"
        "b .Lopen_cfw_hwcfg_return\n"
        ".Lopen_cfw_hwcfg_write_values:\n"
        "ldr r0, [r2, #4]\n"
        "lsls r0, r0, #12\n"
        "lsrs r0, r0, #12\n"
        "ldr.w r1, [pc, #1336]\n"
        "str r0, [r1]\n"
        "ldr r0, [r2, #8]\n"
        "lsls r0, r0, #12\n"
        "lsrs r0, r0, #12\n"
        "ldr.w r1, [pc, #1328]\n"
        "str r0, [r1]\n"
        "ldrb r0, [r2]\n"
        "ldr.w r1, [pc, #1324]\n"
        "str r0, [r1]\n"
        ".Lopen_cfw_hwcfg_success:\n"
        "movs r0, #0\n"
        ".Lopen_cfw_hwcfg_return:\n"
        "bx lr\n"
        ".Lopen_cfw_hwcfg_calculate:\n"
        "cmp r2, #0\n"
        "beq .Lopen_cfw_hwcfg_null\n"
        "vldr s0, [r2, #8]\n"
        "vldr s1, [pc, #384]\n"
        "vcmp.f32 s0, s1\n"
        "vmrs apsr_nzcv, fpscr\n"
        "bne .Lopen_cfw_hwcfg_sentinel\n"
        "vldr s3, [r2]\n"
        "ldr.w r0, [pc, #1236]\n"
        "vldr s0, [r0]\n"
        "vldr s1, [r0, #4]\n"
        "vldr s2, [r0, #8]\n"
        "ldr.w r0, [pc, #1276]\n"
        "vldr s4, [r0]\n"
        "vcmp.f32 s4, #0\n"
        "vmrs apsr_nzcv, fpscr\n"
        "bne .Lopen_cfw_hwcfg_accumulator_ready\n"
        "ldr.w r1, [pc, #1264]\n"
        "str r1, [r0]\n"
        "vadd.f32 s1, s1, s2\n"
        "vldr s2, [r0]\n"
        "vmul.f32 s1, s1, s2\n"
        "vstr s1, [r0]\n"
        "vldr s1, [r0]\n"
        "vadd.f32 s0, s1, s0\n"
        "vstr s0, [r0]\n"
        ".Lopen_cfw_hwcfg_accumulator_ready:\n"
        "vldr s0, [pc, #300]\n"
        "vmul.f32 s0, s3, s0\n"
        "vldr s1, [r0]\n"
        "vadd.f32 s0, s0, s1\n"
        "vldr s1, [pc, #396]\n"
        "vadd.f32 s0, s0, s1\n"
        "vstr s0, [r2, #4]\n"
        "b .Lopen_cfw_hwcfg_success\n"
        ".Lopen_cfw_hwcfg_sentinel:\n"
        "movs r0, #7\n"
        "b .Lopen_cfw_hwcfg_return\n"
        ".Lopen_cfw_hwcfg_null:\n"
        "movs r0, #6\n"
        "b .Lopen_cfw_hwcfg_return\n"
        ".Lopen_cfw_hwcfg_copy_full:\n"
        "cmp r2, #0\n"
        "beq .Lopen_cfw_hwcfg_copy_full_null\n"
        "vldr s0, [r2, #12]\n"
        "vldr s1, [pc, #252]\n"
        "vcmp.f32 s0, s1\n"
        "vmrs apsr_nzcv, fpscr\n"
        "bne .Lopen_cfw_hwcfg_copy_full_sentinel\n"
        "ldr.w r0, [pc, #1108]\n"
        "ldr r1, [r0]\n"
        "str r1, [r2]\n"
        "ldr r1, [r0, #4]\n"
        "str r1, [r2, #4]\n"
        "ldr r1, [r0, #8]\n"
        "str r1, [r2, #8]\n"
        "ldrb r0, [r0, #12]\n"
        "str r0, [r2, #12]\n"
        "b .Lopen_cfw_hwcfg_success\n"
        ".Lopen_cfw_hwcfg_copy_full_sentinel:\n"
        "movs r0, #7\n"
        "b .Lopen_cfw_hwcfg_return\n"
        ".Lopen_cfw_hwcfg_copy_full_null:\n"
        "movs r0, #6\n"
        "b .Lopen_cfw_hwcfg_return\n"
        ".Lopen_cfw_hwcfg_copy_pair:\n"
        "cmp r2, #0\n"
        "beq .Lopen_cfw_hwcfg_copy_pair_null\n"
        "movs r0, r2\n"
        "vldr s0, [r0, #12]\n"
        "vldr s1, [pc, #196]\n"
        "vcmp.f32 s0, s1\n"
        "vmrs apsr_nzcv, fpscr\n"
        "bne .Lopen_cfw_hwcfg_copy_pair_sentinel\n"
        "ldr.w r1, [pc, #1072]\n"
        "ldr r3, [r1]\n"
        "str r3, [r0]\n"
        "ldr r1, [r1, #4]\n"
        "str r1, [r0, #4]\n"
        "movs r0, #0\n"
        "str r0, [r2, #8]\n"
        "movs r0, #0\n"
        "str r0, [r2, #12]\n"
        "b .Lopen_cfw_hwcfg_success\n"
        ".Lopen_cfw_hwcfg_copy_pair_sentinel:\n"
        "movs r0, #7\n"
        "b .Lopen_cfw_hwcfg_return\n"
        ".Lopen_cfw_hwcfg_copy_pair_null:\n"
        "movs r0, #6\n"
        "b .Lopen_cfw_hwcfg_return\n"
        ".Lopen_cfw_hwcfg_bad_operation:\n"
        "movs r0, #6\n"
        "b .Lopen_cfw_hwcfg_return\n"
    );
}

__attribute__((used, noinline, naked, visibility("default"), pcs("aapcs-vfp")))
open_cfw_hwcfg_u32 open_cfw_bootloader_hw_channel_normalize_42ee00(
    open_cfw_hwcfg_u32 value, open_cfw_hwcfg_u32 enabled)
{
    __asm volatile(
        "ldr.w r2, [pc, #884]\n"
        "ldrb r2, [r2]\n"
        "cmp r2, #0\n"
        "beq .Lopen_cfw_normalize_return\n"
        "uxtb r1, r1\n"
        "cmp r1, #0\n"
        "beq .Lopen_cfw_normalize_return\n"
        "ubfx r2, r0, #6, #14\n"
        "movw r1, #1190\n"
        "muls r2, r1, r2\n"
        "lsrs r2, r2, #12\n"
        "vmov s0, r2\n"
        "vcvt.f32.u32 s0, s0\n"
        "ldr.w r1, [pc, #840]\n"
        "vmov.f32 s1, #1.0\n"
        "vldr s2, [r1, #4]\n"
        "vsub.f32 s1, s1, s2\n"
        "vdiv.f32 s0, s0, s1\n"
        "vldr s1, [r1]\n"
        "vldr s2, [pc, #468]\n"
        "vmla.f32 s0, s1, s2\n"
        "vldr s1, [pc, #464]\n"
        "vmul.f32 s0, s0, s1\n"
        "vldr s1, [pc, #460]\n"
        "vdiv.f32 s0, s0, s1\n"
        "lsrs r0, r0, #20\n"
        "lsls r0, r0, #20\n"
        "movs r1, r0\n"
        "vcvt.u32.f32 s0, s0\n"
        "vmov r0, s0\n"
        "lsls r0, r0, #6\n"
        "lsls r0, r0, #14\n"
        "lsrs r0, r0, #14\n"
        "orrs r0, r1\n"
        ".Lopen_cfw_normalize_return:\n"
        "bx lr\n"
    );
}

__attribute__((used, noinline, naked, visibility("default"), pcs("aapcs-vfp")))
open_cfw_hwcfg_u32 open_cfw_bootloader_hw_channel_enumerate_42ee70(
    open_cfw_hwcfg_u32 *handle, open_cfw_hwcfg_u32 wide_value,
    const open_cfw_hwcfg_u32 *input, open_cfw_hwcfg_u32 *count,
    open_cfw_hwcfg_u32 *output)
{
    __asm volatile(
        "push.w {r3, r4, r5, r6, r7, r8, r9, lr}\n"
        "mov r8, r1\n"
        "movs r5, r2\n"
        "movs r6, r3\n"
        "ldr r7, [r6]\n"
        "ldr r1, [r0, #4]\n"
        "cmp r0, #0\n"
        "beq .Lopen_cfw_enumerate_invalid_handle\n"
        "ldr r0, [r0]\n"
        "bic r0, r0, #0xfe000000\n"
        "ldr r1, [pc, #752]\n"
        "cmp r0, r1\n"
        "beq .Lopen_cfw_enumerate_output\n"
        ".Lopen_cfw_enumerate_invalid_handle:\n"
        "movs r0, #2\n"
        "b .Lopen_cfw_enumerate_return\n"
        ".Lopen_cfw_enumerate_output:\n"
        "ldr r4, [sp, #32]\n"
        "cmp r4, #0\n"
        "bne .Lopen_cfw_enumerate_begin\n"
        "movs r0, #6\n"
        "b .Lopen_cfw_enumerate_return\n"
        ".Lopen_cfw_enumerate_begin:\n"
        "movs r0, #0\n"
        "str r0, [r6]\n"
        "cmp r5, #0\n"
        "bne .Lopen_cfw_enumerate_input_mode\n"
        ".Lopen_cfw_enumerate_hardware_loop:\n"
        "ldr.w r0, [pc, #764]\n"
        "ldr r0, [r0]\n"
        "ubfx r1, r0, #28, #3\n"
        "ldr r2, [pc, #724]\n"
        "adds.w r2, r2, r1, lsl #2\n"
        "ldr r1, [r2]\n"
        "ubfx r1, r1, #8, #4\n"
        "cmp r1, #8\n"
        "bne .Lopen_cfw_enumerate_not_eight\n"
        "movs r1, #1\n"
        "b .Lopen_cfw_enumerate_eight_ready\n"
        ".Lopen_cfw_enumerate_not_eight:\n"
        "movs r1, #0\n"
        ".Lopen_cfw_enumerate_eight_ready:\n"
        "eors r1, r1, #1\n"
        "uxtb r1, r1\n"
        "bl open_cfw_bootloader_hw_channel_normalize_42ee00\n"
        "ubfx r1, r0, #28, #3\n"
        "str r1, [r4, #4]\n"
        "mov r1, r8\n"
        "uxtb r1, r1\n"
        "cmp r1, #0\n"
        "beq .Lopen_cfw_enumerate_narrow\n"
        "lsls r1, r0, #12\n"
        "lsrs r1, r1, #12\n"
        "b .Lopen_cfw_enumerate_store\n"
        ".Lopen_cfw_enumerate_narrow:\n"
        "ubfx r1, r0, #6, #14\n"
        ".Lopen_cfw_enumerate_store:\n"
        "str r1, [r4]\n"
        "adds r4, #8\n"
        "ldr r1, [r6]\n"
        "adds r1, r1, #1\n"
        "str r1, [r6]\n"
        "ubfx r0, r0, #20, #8\n"
        "cmp r0, #0\n"
        "beq .Lopen_cfw_enumerate_success\n"
        "ldr r0, [r6]\n"
        "cmp r0, r7\n"
        "blo .Lopen_cfw_enumerate_hardware_loop\n"
        "b .Lopen_cfw_enumerate_success\n"
        ".Lopen_cfw_enumerate_input_mode:\n"
        "movs.w r9, #0\n"
        "ldr r0, [pc, #636]\nldr r0, [r0]\nubfx r0, r0, #8, #4\ncmp r0, #8\nbne 1f\nmovs r0, #1\nb 2f\n1:\nmovs r0, #0\n2:\norrs.w r9, r0, r9\n"
        "ldr r0, [pc, #652]\nldr r0, [r0]\nubfx r0, r0, #8, #4\ncmp r0, #8\nbne 3f\nmovs r0, #2\nb 4f\n3:\nmovs r0, #0\n4:\norrs.w r9, r0, r9\n"
        "ldr r0, [pc, #632]\nldr r0, [r0]\nubfx r0, r0, #8, #4\ncmp r0, #8\nbne 5f\nmovs r0, #4\nb 6f\n5:\nmovs r0, #0\n6:\norrs.w r9, r0, r9\n"
        "ldr r0, [pc, #616]\nldr r0, [r0]\nubfx r0, r0, #8, #4\ncmp r0, #8\nbne 7f\nmovs r0, #8\nb 8f\n7:\nmovs r0, #0\n8:\norrs.w r9, r0, r9\n"
        "ldr r0, [pc, #596]\nldr r0, [r0]\nubfx r0, r0, #8, #4\ncmp r0, #8\nbne 9f\nmovs r0, #16\nb 10f\n9:\nmovs r0, #0\n10:\norrs.w r9, r0, r9\n"
        "ldr r0, [pc, #580]\nldr r0, [r0]\nubfx r0, r0, #8, #4\ncmp r0, #8\nbne 11f\nmovs r0, #32\nb 12f\n11:\nmovs r0, #0\n12:\norrs.w r9, r0, r9\n"
        "ldr r0, [pc, #560]\nldr r0, [r0]\nubfx r0, r0, #8, #4\ncmp r0, #8\nbne 13f\nmovs r0, #64\nb 14f\n13:\nmovs r0, #0\n14:\norrs.w r9, r0, r9\n"
        "ldr r0, [pc, #544]\nldr r0, [r0]\nubfx r0, r0, #8, #4\ncmp r0, #8\nbne 15f\nmovs r0, #128\nb 16f\n15:\nmovs r0, #0\n16:\norrs.w r9, r0, r9\n"
        ".Lopen_cfw_enumerate_input_loop:\n"
        "ldr r0, [r5]\n"
        "ubfx r8, r0, #28, #3\n"
        "ldr r0, [r5]\n"
        "lsls r0, r0, #12\n"
        "lsrs r0, r0, #12\n"
        "mov r1, r9\n"
        "lsrs.w r1, r1, r8\n"
        "ands r1, r1, #1\n"
        "eors r1, r1, #1\n"
        "uxtb r1, r1\n"
        "bl open_cfw_bootloader_hw_channel_normalize_42ee00\n"
        "ubfx r0, r0, #6, #14\n"
        "str r0, [r4]\n"
        "str.w r8, [r4, #4]\n"
        "adds r5, r5, #4\n"
        "adds r4, #8\n"
        "ldr r0, [r6]\n"
        "adds r0, r0, #1\n"
        "str r0, [r6]\n"
        "ldr r0, [r6]\n"
        "cmp r0, r7\n"
        "blo .Lopen_cfw_enumerate_input_loop\n"
        ".Lopen_cfw_enumerate_success:\n"
        "movs r0, #0\n"
        ".Lopen_cfw_enumerate_return:\n"
        "pop.w {r1, r4, r5, r6, r7, r8, r9, pc}\n"
    );
}

#else

typedef struct open_cfw_hwcfg_handle { open_cfw_hwcfg_u32 word0, word1; } open_cfw_hwcfg_handle;
typedef struct open_cfw_hwcfg_quad { open_cfw_hwcfg_u32 word[4]; } open_cfw_hwcfg_quad;
typedef struct open_cfw_hwcfg_pair { open_cfw_hwcfg_u32 value, channel; } open_cfw_hwcfg_pair;
typedef struct open_cfw_hwcfg_model {
    open_cfw_hwcfg_u32 limit0, limit1, selector;
    float calibration[4]; float pair[2]; float accumulator;
    open_cfw_hwcfg_u32 channels[8], traversal;
    open_cfw_hwcfg_u8 normalize_enabled;
} open_cfw_hwcfg_model;

static float open_cfw_hwcfg_bits_to_float(open_cfw_hwcfg_u32 bits) {
    union { open_cfw_hwcfg_u32 u; float f; } value; value.u=bits; return value.f;
}
static open_cfw_hwcfg_u32 open_cfw_hwcfg_float_to_bits(float number) {
    union { open_cfw_hwcfg_u32 u; float f; } value; value.f=number; return value.u;
}

__attribute__((used,noinline,visibility("default")))
open_cfw_hwcfg_u32 open_cfw_bootloader_hw_config_dispatch_42ec0c_portable(
    const open_cfw_hwcfg_handle *handle, open_cfw_hwcfg_u32 operation,
    open_cfw_hwcfg_quad *config, open_cfw_hwcfg_model *model)
{
    if (handle==(const open_cfw_hwcfg_handle *)0 ||
        (handle->word0 & ~0xFE000000U)!=OPEN_CFW_HWCFG_MAGIC) return 2U;
    switch ((open_cfw_hwcfg_u8)operation) {
    case 0U:
        if (config->word[1]>=0x100000U || config->word[2]>=0x100000U) return 5U;
        model->limit0=config->word[1]&0xFFFFFU; model->limit1=config->word[2]&0xFFFFFU;
        model->selector=config->word[0]&0xFFU; return 0U;
    case 1U:
        if (config==(open_cfw_hwcfg_quad *)0) return 6U;
        if (config->word[2]!=0xC2F6E979U) return 7U;
        if (model->accumulator==0.0f)
            model->accumulator=-290.0f+(model->calibration[1]+model->calibration[2])*-290.0f+model->calibration[0];
        config->word[1]=open_cfw_hwcfg_float_to_bits(open_cfw_hwcfg_bits_to_float(config->word[0])*290.0f+model->accumulator-273.15f); return 0U;
    case 2U:
        if (config==(open_cfw_hwcfg_quad *)0) return 6U;
        if (config->word[3]!=0xC2F6E979U) return 7U;
        config->word[0]=open_cfw_hwcfg_float_to_bits(model->calibration[0]);
        config->word[1]=open_cfw_hwcfg_float_to_bits(model->calibration[1]);
        config->word[2]=open_cfw_hwcfg_float_to_bits(model->calibration[2]);
        config->word[3]=open_cfw_hwcfg_float_to_bits(model->calibration[3])&0xFFU; return 0U;
    case 3U:
        if (config==(open_cfw_hwcfg_quad *)0) return 6U;
        if (config->word[3]!=0xC2F6E979U) return 7U;
        config->word[0]=open_cfw_hwcfg_float_to_bits(model->pair[0]);config->word[1]=open_cfw_hwcfg_float_to_bits(model->pair[1]);config->word[2]=0U;config->word[3]=0U;return 0U;
    default:return 6U;
    }
}

__attribute__((used,noinline,visibility("default")))
open_cfw_hwcfg_u32 open_cfw_bootloader_hw_channel_normalize_42ee00_portable(
    open_cfw_hwcfg_u32 value, open_cfw_hwcfg_u32 enabled,
    const open_cfw_hwcfg_model *model)
{
    open_cfw_hwcfg_u32 scaled;
    float number;
    if (model->normalize_enabled==0U || (open_cfw_hwcfg_u8)enabled==0U) return value;
    scaled=((value>>6)&0x3FFFU)*1190U>>12;
    number=((float)scaled/(1.0f-model->pair[1])+model->pair[0]*-1000.0f)*4096.0f/1190.0f;
    scaled=(open_cfw_hwcfg_u32)number;
    return (value&0xFFF00000U)|((scaled&0xFFFU)<<6);
}

__attribute__((used,noinline,visibility("default")))
open_cfw_hwcfg_u32 open_cfw_bootloader_hw_channel_enumerate_42ee70_portable(
    const open_cfw_hwcfg_handle *handle, open_cfw_hwcfg_u32 wide_value,
    const open_cfw_hwcfg_u32 *input, open_cfw_hwcfg_u32 *count,
    open_cfw_hwcfg_pair *output, const open_cfw_hwcfg_model *model)
{
    open_cfw_hwcfg_u32 limit=*count,index,value,mask=0U;
    if (handle==(const open_cfw_hwcfg_handle *)0 ||
        (handle->word0&~0xFE000000U)!=OPEN_CFW_HWCFG_MAGIC) return 2U;
    if (output==(open_cfw_hwcfg_pair *)0) return 6U; *count=0U;
    if (input==(const open_cfw_hwcfg_u32 *)0) {
        do { value=model->traversal;index=(value>>28)&7U;
            value=open_cfw_bootloader_hw_channel_normalize_42ee00_portable(value,((model->channels[index]>>8)&15U)!=8U,model);
            output->channel=(value>>28)&7U;output->value=(open_cfw_hwcfg_u8)wide_value?(value&0xFFFFFU):((value>>6)&0x3FFFU);
            ++output;++*count;
        } while (((value>>20)&0xFFU)!=0U && *count<limit); return 0U;
    }
    for(index=0U;index<8U;++index) if (((model->channels[index]>>8)&15U)==8U) mask|=1U<<index;
    do { value=*input++;index=(value>>28)&7U;
        value=open_cfw_bootloader_hw_channel_normalize_42ee00_portable(value&0xFFFFFU,((mask>>index)&1U)^1U,model);
        output->value=(value>>6)&0x3FFFU;output->channel=index;++output;++*count;
    } while (*count<limit); return 0U;
}
#endif
