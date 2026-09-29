
undefined8 FUN_0046713e(uint param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  uVar3 = param_1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    if (param_1 == 0) {
      param_3 = 0x4672e0;
    }
    else {
      param_3 = 0x4672dc;
    }
    uVar3 = 0x1be;
    param_2 = PTR_s__Setting__Handle_silent_mode_fro_00467c24;
    FUN_0043d574(3,PTR_s_setting_004672f0,PTR_s_D__01_workspace_s200_ap510b_iar__004672ec,
                 PTR_s_setting_handle_silent_mode_setti_00467c28,0x1be,
                 PTR_s__Setting__Handle_silent_mode_fro_00467c24,param_3,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    if (param_1 == 0) {
      uVar2 = 0x4672e0;
    }
    else {
      uVar2 = 0x4672dc;
    }
    compress_log_output(0xc400000,PTR_s__setting__Setting__Handle_silent_00467e4c,
                        PTR_s__setting__Setting__Handle_silent_00467e4c,uVar2,uVar3,param_2,param_3)
    ;
  }
  SilentMode_SetStatusFromApp(param_1 & 0xff);
  return CONCAT44(param_2,uVar3);
}

