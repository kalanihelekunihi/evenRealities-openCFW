
undefined4 gx8002_app_command_callback_persistent(int param_1)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  char *pcVar4;
  int iVar5;
  undefined *puVar6;
  uint uVar7;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  
  iVar2 = DAT_102096a4;
  if (*(short *)(param_1 + 4) == 0x170) {
    gx8002_printf(PTR_s_receive_misc_test_cmd_102096a8);
    if (*(int *)(iVar2 + 0x28) == 0) {
      uVar3 = gx8002_audio_input_query_vad();
      *(undefined4 *)(iVar2 + 0x28) = uVar3;
    }
    gx8002_app_reply(0,0x70,*(int *)(iVar2 + 0x28) != 0);
  }
  if (*(short *)(param_1 + 4) == 0x171) {
    gx8002_printf(PTR_s_receive_gsensor_test_cmd_102096ac);
    gx8002_gsensor_workstate();
    gx8002_app_reply(0,0x71);
  }
  if (*(short *)(param_1 + 4) == 0x102) {
    gx8002_printf(PTR_s_receive_version_req_102096b0);
    iVar2 = DAT_102096a4;
    uStack_1c = DAT_102096b4;
    uStack_18 = DAT_102096b8;
    pcVar4 = (char *)gx8002_strtok(&uStack_1c,PTR_DAT_102096bc);
    puVar6 = PTR_DAT_102096bc;
    *(char *)(iVar2 + 0x2f) = *pcVar4 + -0x30;
    pcVar4 = (char *)gx8002_strtok(0,puVar6);
    puVar6 = PTR_DAT_102096bc;
    *(char *)(iVar2 + 0x2e) = *pcVar4 + -0x30;
    pcVar4 = (char *)gx8002_strtok(0,puVar6);
    puVar6 = PTR_DAT_102096bc;
    *(char *)(iVar2 + 0x2d) = *pcVar4 + -0x30;
    pcVar4 = (char *)gx8002_strtok(0,puVar6);
    iVar5 = DAT_102096c0;
    cVar1 = *pcVar4;
    *(char *)(iVar2 + 0x2c) = cVar1 + -0x30;
    *(char *)(iVar2 + 0x33) = cVar1 + -0x30;
    *(undefined1 *)(iVar2 + 0x30) = *(undefined1 *)(iVar2 + 0x2f);
    *(undefined2 *)(iVar5 + 4) = 0x202;
    *(undefined1 *)(iVar2 + 0x31) = *(undefined1 *)(iVar2 + 0x2e);
    *(undefined1 *)(iVar5 + 7) = 1;
    *(undefined1 *)(iVar2 + 0x32) = *(undefined1 *)(iVar2 + 0x2d);
    *(int *)(iVar5 + 0x10) = iVar2 + 0x30;
    *(undefined4 *)(iVar5 + 0x18) = 4;
    UartMessageAsyncSend();
  }
  if (*(short *)(param_1 + 4) == 0x107) {
    gx8002_printf(PTR_s_receive_switch_bf_req_102096c4);
    gx8002_app_reply(0,7,1);
    gx_gpio_set_direction(0);
    gx_gpio_set_direction(1,0);
    gx8002_multiboot_switch();
  }
  if (*(short *)(param_1 + 4) == 0x109) {
    gx8002_printf(PTR_s_open_vad_reporting_102096c8);
    gx8002_app_reply(0,9,1);
    *(undefined2 *)(DAT_102096a4 + 0x34) = 1;
  }
  if (*(short *)(param_1 + 4) == 0x10a) {
    gx8002_printf(PTR_s_close_vad_reporting_102096cc);
    gx8002_app_reply(0,10,1);
    *(undefined2 *)(DAT_102096a4 + 0x34) = 0;
  }
  puVar6 = PTR_LAB_102096d0;
  iVar2 = DAT_102096a4;
  if (*(short *)(param_1 + 4) != 0x10b) goto LAB_102095b6;
  for (uVar7 = 0; uVar7 < *(uint *)(param_1 + 0x18); uVar7 = uVar7 + 1) {
    gx8002_printf(puVar6,*(undefined1 *)(*(int *)(param_1 + 0x10) + uVar7));
    *(uint *)(iVar2 + 0x38) = (uint)*(byte *)(*(int *)(param_1 + 0x10) + uVar7);
  }
  uVar7 = *(uint *)(iVar2 + 0x38);
  puVar6 = PTR_DAT_102096f8;
  if (uVar7 < 0x31) {
    iVar5 = gx_audio_in_set_rough_gain(2);
    uVar7 = *(uint *)(iVar2 + 0x38);
    puVar6 = PTR_s_set_pga_gain__d_fail_102096f4;
    if (iVar5 != 0) goto LAB_10209694;
    gx8002_printf(PTR_s_set_pga_gain__d_success_102096d4,uVar7);
    uVar3 = 1;
  }
  else {
LAB_10209694:
    gx8002_printf(puVar6,uVar7);
    uVar3 = 0;
  }
  gx8002_app_reply(0,0xb,uVar3);
LAB_102095b6:
  if (*(short *)(param_1 + 4) == 0x10c) {
    gx8002_printf(PTR_s_receive_open_dmic_req_102096d8);
    gx8002_printf(PTR_s_dmic_init_master_102096dc);
    gx8002_padmux_set(0,7);
    gx8002_padmux_set(1,9);
    gx8002_app_reply(0,0xc,1);
  }
  if (*(short *)(param_1 + 4) == 0x10d) {
    gx8002_printf(PTR_s_receive_close_dmic_req_102096e0);
    gx8002_printf(PTR_s_dmic_close_master_102096e4);
    gx8002_padmux_set(0,1);
    gx8002_padmux_set(1);
    gx_gpio_set_direction(0);
    gx_gpio_set_direction(1,0);
    gx8002_app_reply(0,0xd,1);
  }
  if (*(short *)(param_1 + 4) == 0x10e) {
    gx8002_printf(PTR_s_receive_set_pdm_ch_delay_req_102096e8);
    uStack_1c = CONCAT31(uStack_1c._1_3_,1);
    gx8002_audio_channel_field(0,1);
    iVar2 = DAT_102096c0;
    *(undefined2 *)(DAT_102096c0 + 4) = *(undefined2 *)(param_1 + 4);
    *(undefined1 *)(iVar2 + 7) = 1;
    *(undefined4 **)(iVar2 + 0x10) = &uStack_1c;
    *(undefined4 *)(iVar2 + 0x18) = 1;
    UartMessageAsyncSend();
  }
  if (*(short *)(param_1 + 4) == 0x10f) {
    gx8002_printf(PTR_s_receive_set_i2s_status_req_102096ec);
    iVar2 = DAT_102096a4;
    *(undefined4 *)(DAT_102096a4 + 0x3c) = 1;
    puVar6 = PTR_s_i2s_mode_state__d_102096f0;
    *(undefined1 *)(iVar2 + 0x40) = **(undefined1 **)(param_1 + 0x10);
    gx8002_printf(puVar6);
  }
  return 0;
}

