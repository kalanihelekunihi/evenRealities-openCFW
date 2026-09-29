
undefined8
SVC_Settings_HeadUpConfig(undefined4 param_1,undefined4 param_2,int param_3,undefined *param_4)

{
  int iVar1;
  char *pcVar2;
  int iStack_10;
  undefined *puStack_c;
  
  iStack_10 = param_3;
  puStack_c = param_4;
  iVar1 = FUN_0045a568();
  if (iVar1 == 1) {
    pcVar2 = DAT_0046c6a8;
    if (*DAT_0046c6a8 == '\0') {
      pcVar2 = *(char **)(DAT_0046c694 + 4);
    }
    if (pcVar2[10] == '\x01') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        puStack_c = PTR_s_head_up_switch_open__open_head_u_0046c718;
        iStack_10 = 0x241;
        FUN_0043d574(3,PTR_s_service_settings_0046c664,DAT_0046c660,
                     PTR_s_SVC_Settings_HeadUpConfig_0046c71c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__service_settings_head_up_switch_0046c720,
                            PTR_s__service_settings_head_up_switch_0046c720);
      }
      HUB_Open(1);
      puStack_c = *(undefined **)(PTR_DAT_0046c724 + 4);
      iStack_10 = *(int *)(pcVar2 + 0x10) + *(int *)(pcVar2 + 0xc);
      if (0x5a < iStack_10) {
        iStack_10 = 0x5a;
      }
      if (iStack_10 < -0x5a) {
        iStack_10 = -0x5a;
      }
      HUB_ParameterConfig(1,&iStack_10);
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        puStack_c = PTR_s_head_up_switch_close__close_head_0046c728;
        iStack_10 = 0x24c;
        FUN_0043d574(3,PTR_s_service_settings_0046c664,DAT_0046c660,
                     PTR_s_SVC_Settings_HeadUpConfig_0046c71c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__service_settings_head_up_switch_0046c72c);
      }
      HUB_Close(1);
    }
  }
  return CONCAT44(puStack_c,iStack_10);
}

