
undefined8 FUN_00466abc(int param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  ushort uVar1;
  int iVar2;
  int iVar3;
  
  if (param_1 == 0) {
    iVar2 = FUN_0043d0ce();
    iVar3 = param_1;
    if (iVar2 << 0x1e < 0) {
      iVar3 = 0x9d;
      param_2 = PTR_s_pMessage_is_NULL_00467300;
      FUN_0043d574(2,PTR_s_setting_004672f0,PTR_s_D__01_workspace_s200_ap510b_iar__004672ec,
                   PTR_s_setting_handle_device_receive_in_004674c8,0x9d,
                   PTR_s_pMessage_is_NULL_00467300,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__setting_pMessage_is_NULL_004674ac,
                          PTR_s__setting_pMessage_is_NULL_004674ac);
    }
    goto LAB_00466bea;
  }
  uVar1 = *(ushort *)(param_1 + 0xc);
  if (uVar1 == 1) {
    FUN_00466bec(param_1 + 0x10);
    iVar3 = param_1;
  }
  else {
    iVar3 = param_1;
    if (uVar1 == 0) {
LAB_00466b9a:
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        iVar3 = 0xe0;
        param_2 = PTR_s_Unknown_setting_type___d_004674cc;
        FUN_0043d574(2,PTR_s_setting_004672f0,PTR_s_D__01_workspace_s200_ap510b_iar__004672ec,
                     PTR_s_setting_handle_device_receive_in_004674c8,0xe0,
                     PTR_s_Unknown_setting_type___d_004674cc,*(undefined2 *)(param_1 + 0xc));
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__setting_Unknown_setting_type____004674d0,
                            PTR_s__setting_Unknown_setting_type____004674d0,
                            *(undefined2 *)(param_1 + 0xc));
      }
    }
    else if (uVar1 == 3) {
      FUN_00466ea2(*(undefined4 *)(param_1 + 0x10));
      iVar3 = param_1;
    }
    else if (uVar1 < 3) {
      FUN_00466e1c(*(undefined4 *)(param_1 + 0x10));
      iVar3 = param_1;
    }
    else if (uVar1 == 5) {
      FUN_00467134(*(undefined4 *)(param_1 + 0x10));
      iVar3 = param_1;
    }
    else if (uVar1 < 5) {
      FUN_00466f28(param_1 + 0x10);
      iVar3 = param_1;
    }
    else if (uVar1 != 7) {
      if (uVar1 < 7) {
        FUN_0046713e(*(undefined4 *)(param_1 + 0x10));
        iVar3 = param_1;
      }
      else if (uVar1 == 9) {
        FUN_00467206(param_1 + 0x10);
        iVar3 = param_1;
      }
      else if (uVar1 < 9) {
        FUN_004671a2(*(undefined4 *)(param_1 + 0x10));
        iVar3 = param_1;
      }
      else if (uVar1 == 0xb) {
        FUN_00467540(param_1 + 0x10);
        iVar3 = param_1;
      }
      else if (uVar1 < 0xb) {
        FUN_00467308(param_1 + 0x10);
        iVar3 = param_1;
      }
      else {
        if (uVar1 != 0xc) goto LAB_00466b9a;
        FUN_00467c34(param_1 + 0x10);
        iVar3 = param_1;
      }
    }
  }
  SVC_Settings_SaveSettingConfigToKVCheck();
  FUN_00466016();
LAB_00466bea:
  return CONCAT44(param_2,iVar3);
}

