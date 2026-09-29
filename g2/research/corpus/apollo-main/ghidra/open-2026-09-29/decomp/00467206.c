
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00467206(undefined4 *param_1)

{
  int iVar1;
  int iVar2;
  
  if (param_1 == (undefined4 *)0x0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,PTR_s_setting_004672f0,PTR_s_D__01_workspace_s200_ap510b_iar__004672ec,
                   PTR_s_setting_handle_unit_setting_00467d5c,0x1e9,PTR_s_unit_data_is_NULL_00467d58
                  );
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__setting_unit_data_is_NULL_00467d60,
                          PTR_s__setting_unit_data_is_NULL_00467d60);
    }
  }
  else {
    iVar1 = FUN_00466010();
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_setting_004672f0,PTR_s_D__01_workspace_s200_ap510b_iar__004672ec,
                   PTR_s_setting_handle_unit_setting_00467d5c,500,
                   PTR_s_Received_universal_unit_setting__00467d64,*param_1,param_1[1],param_1[2],
                   param_1[3],param_1[4]);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xd400000,_DAT_00467f04,_DAT_00467f04,*param_1,param_1[1],param_1[2],
                          param_1[3],param_1[4]);
    }
    *(char *)(iVar1 + 1) = (char)*param_1;
    *(char *)(iVar1 + 2) = (char)param_1[3];
    *(char *)(iVar1 + 3) = (char)param_1[1];
    *(undefined4 *)(iVar1 + 0x18) = param_1[2];
    *(char *)(iVar1 + 4) = (char)param_1[4];
    FUN_004661a6();
  }
  return;
}

