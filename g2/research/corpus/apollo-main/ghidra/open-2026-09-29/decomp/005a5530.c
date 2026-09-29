
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 _atRM(undefined4 param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = param_1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uVar2 = 0x13;
    param_2 = PTR_s_RM__s_005a56e0;
    param_3 = param_1;
    FUN_0043d574(4,PTR_s_at_fs_005a56ec,PTR_s_D__01_workspace_s200_ap510b_iar__005a56e8,
                 PTR_s__atRM_005a56e4,0x13,PTR_s_RM__s_005a56e0,param_1,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__at_fs_RM__s_005a56f0,PTR_s__at_fs_RM__s_005a56f0,param_1,
                        uVar2,param_2,param_3);
  }
  if (*DAT_005a56f4 == 1) {
    iVar1 = file_remove(param_1);
    if (iVar1 == 0) {
      at_core_output(_DAT_005a56fc);
      uVar2 = 1;
    }
    else {
      at_core_output(_DAT_005a56f8,param_1);
      uVar2 = 0;
    }
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

