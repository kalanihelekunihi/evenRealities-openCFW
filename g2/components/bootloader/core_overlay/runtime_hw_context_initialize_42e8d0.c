/* SPDX-License-Identifier: MIT */
/* Clean-room hardware-context slot and calibration-profile initializer. */
typedef __UINT8_TYPE__ open_cfw_hw_init_u8;
typedef __UINT32_TYPE__ open_cfw_hw_init_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_config_read_421548(void);
__attribute__((used,noinline,naked,visibility("default")))
open_cfw_hw_init_u32 open_cfw_bootloader_hw_context_initialize_42e8d0(void)
{
    __asm volatile(
        "push {r3,r4,r5,r6,r7,lr}\ncmp r0,#0\nbeq index_invalid\nmovs r0,#5\nb finish\n"
        "index_invalid:\ncmp r1,#0\nbne validate_slot\nmovs r0,#6\nb finish\n"
        "validate_slot:\nmovs r3,#0x48\nldr.w r4,[pc,#0x868]\nmul r2,r3,r0\n"
        "ldr r2,[r4,r2]\nubfx r2,r2,#0x18,#1\ncmp r2,#0\nbeq claim_slot\n"
        "movs r0,#7\nb finish\nclaim_slot:\nmul r2,r3,r0\nadd r2,r4\nldr r5,[r2]\n"
        "orrs r5,r5,#0x1000000\nstr r5,[r2]\nmul r2,r3,r0\nadd r2,r4\n"
        "ldr r5,[r2]\nands r5,r5,#0xff000000\norr r5,r5,#0xaf00af\n"
        "orrs r5,r5,#0xaf00\nstr r5,[r2]\nmul r2,r3,r0\nadd r2,r4\n"
        "str r0,[r2,#4]\nmovs r2,#0\nldr.w r5,[pc,#0x828]\nstr r2,[r5]\n"
        "muls r0,r3,r0\nadd r0,r4\nstr r0,[r1]\nldr.w r4,[pc,#0x820]\n"
        "ldr.w r5,[pc,#0x820]\nldr r0,[r5]\ncmp r0,r4\nbne read_primary_profile\n"
        "ldr.w r0,[pc,#0x81c]\nldr r1,[r5,#0x38]\nstr r1,[r0]\nldr r1,[r5,#0x3c]\n"
        "str r1,[r0,#4]\nldr r1,[r5,#0x40]\nstr r1,[r0,#8]\nmovs r0,#0\nb validate_primary\n"
        "read_primary_profile:\nldr.w r7,[pc,#0x808]\nmovs r3,r7\nmovs r2,#1\n"
        "mov.w r1,#0x240\nmovs r0,#1\nbl open_cfw_bootloader_config_read_421548\n"
        "movs r6,r0\nadds r3,r7,#4\nmovs r2,#1\nmovw r1,#0x241\n"
        "movs r0,#1\nbl open_cfw_bootloader_config_read_421548\norrs r6,r0\n"
        "adds.w r3,r7,#8\nmovs r2,#1\nmovw r1,#0x242\nmovs r0,#1\n"
        "bl open_cfw_bootloader_config_read_421548\norrs r0,r6\nvalidate_primary:\n"
        "ldr.w r2,[pc,#0x7d0]\nldr r1,[r2]\ncmp r1,#0\nbeq primary_default\n"
        "ldr r1,[r2,#4]\ncmp r1,#0\nbeq primary_default\nldr r1,[r2,#8]\ncmp r1,#0\n"
        "beq primary_default\ncmp r0,#0\nbeq primary_valid\nprimary_default:\n"
        "ldr.w r0,[pc,#0x7bc]\nstr r0,[r2]\nldr.w r0,[pc,#0x7b8]\nstr r0,[r2,#4]\n"
        "ldr.w r0,[pc,#0x7b8]\nstr r0,[r2,#8]\nmovs r0,#0\nstrb r0,[r2,#0xc]\n"
        "b primary_done\nprimary_valid:\nmovs r0,#1\nstrb r0,[r2,#0xc]\nprimary_done:\n"
        "ldr r0,[r5]\ncmp r0,r4\nbne read_secondary_profile\nldr.w r0,[pc,#0x7a4]\n"
        "ldr r1,[r5,#0x48]\nstr r1,[r0,#4]\nldr r1,[r5,#0x4c]\nstr r1,[r0]\n"
        "movs r0,#0\nb validate_secondary\nread_secondary_profile:\nldr.w r5,[pc,#0x794]\n"
        "adds r3,r5,#4\nmovs r2,#1\nmovw r1,#0x24a\nmovs r0,#1\n"
        "bl open_cfw_bootloader_config_read_421548\nmovs r4,r0\nmovs r3,r5\nmovs r2,#1\n"
        "movw r1,#0x24b\nmovs r0,#1\nbl open_cfw_bootloader_config_read_421548\n"
        "orrs r0,r4\nvalidate_secondary:\nldr.w r1,[pc,#0x774]\nldr r2,[r1]\n"
        "lsrs r2,r2,#1\nlsls r2,r2,#1\nstr r2,[r1]\nldr.w r2,[pc,#0x764]\n"
        "ldr r1,[r2,#4]\ncmp r1,#0\nbeq secondary_invalid\nldr r1,[r2]\ncmp r1,#0\n"
        "beq secondary_invalid\ncmp r0,#0\nbeq secondary_valid\nsecondary_invalid:\n"
        "movs r0,#0\nldr.w r1,[pc,#0x758]\nstrb r0,[r1]\nb success\n"
        "secondary_valid:\nmovs r0,#1\nldr.w r1,[pc,#0x74c]\nstrb r0,[r1]\n"
        "success:\nmovs r0,#0\nfinish:\npop {r1,r4,r5,r6,r7,pc}\n");
}
#else
typedef struct {
    open_cfw_hw_init_u32 slot_word;
    open_cfw_hw_init_u32 slot_index;
    open_cfw_hw_init_u32 retained_magic;
    open_cfw_hw_init_u32 retained_primary[3];
    open_cfw_hw_init_u32 retained_secondary[2];
    open_cfw_hw_init_u32 read_status[5];
    open_cfw_hw_init_u32 read_primary[3];
    open_cfw_hw_init_u32 read_secondary[2];
    open_cfw_hw_init_u32 primary[3];
    open_cfw_hw_init_u32 secondary[2];
    open_cfw_hw_init_u32 control_register;
    open_cfw_hw_init_u32 slot_pointer;
    open_cfw_hw_init_u8 primary_valid;
    open_cfw_hw_init_u8 secondary_valid;
} open_cfw_hw_init_model;

__attribute__((used,noinline,visibility("default")))
open_cfw_hw_init_u32 open_cfw_bootloader_hw_context_initialize_42e8d0_portable(
    open_cfw_hw_init_u32 index, open_cfw_hw_init_u32 output_present,
    open_cfw_hw_init_model *model)
{
    open_cfw_hw_init_u32 status;
    if (index != 0U) return 5U;
    if (output_present == 0U || model == 0U) return 6U;
    if (((model->slot_word >> 24U) & 1U) != 0U) return 7U;
    model->slot_word = (model->slot_word & 0xFF000000U) | 0x00AFAFAFU;
    model->slot_word |= 0x01000000U;
    model->slot_index = index;
    model->slot_pointer = 0x20026DF0U + 0x48U * index;
    if (model->retained_magic == 0x1F01600DU) {
        model->primary[0]=model->retained_primary[0];model->primary[1]=model->retained_primary[1];model->primary[2]=model->retained_primary[2];status=0U;
    } else {
        model->primary[0]=model->read_primary[0];model->primary[1]=model->read_primary[1];model->primary[2]=model->read_primary[2];status=model->read_status[0]|model->read_status[1]|model->read_status[2];
    }
    if(model->primary[0]==0U||model->primary[1]==0U||model->primary[2]==0U||status!=0U){model->primary[0]=0x4395C000U;model->primary[1]=0x3F839874U;model->primary[2]=0xBB8C47A1U;model->primary_valid=0U;}else model->primary_valid=1U;
    if(model->retained_magic==0x1F01600DU){model->secondary[1]=model->retained_secondary[0];model->secondary[0]=model->retained_secondary[1];status=0U;}else{model->secondary[1]=model->read_secondary[0];model->secondary[0]=model->read_secondary[1];status=model->read_status[3]|model->read_status[4];}
    model->control_register&=~1U;model->secondary_valid=(model->secondary[0]!=0U&&model->secondary[1]!=0U&&status==0U)?1U:0U;return 0U;
}
#endif
