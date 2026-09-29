
undefined4 setting_respond_with_local_data(int param_1,int *param_2)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  undefined1 auStack_38 [12];
  int local_2c;
  undefined1 auStack_24 [20];
  
  iVar3 = DAT_0049bdf0;
  if (((param_1 == 0) || (param_2 == (int *)0x0)) || (*param_2 == 0)) {
    uVar1 = 0;
  }
  else {
    iVar2 = setting_build_full_status_package(DAT_0049bdf0);
    if (iVar2 == 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0049bbc0,DAT_0049bbbc,DAT_0049bfd8,0x103,DAT_0049bfd4);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0049bfdc);
      }
      uVar1 = 0;
    }
    else {
      *(undefined4 *)(iVar3 + 4) = *DAT_0049bbf4;
      FUN_004905f4(auStack_24,param_1,*param_2);
      FUN_00439c04(auStack_38,auStack_24,0x14);
      iVar2 = FUN_00490c32(auStack_38,DAT_0049bbd0,iVar3);
      if (iVar2 == 0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0049bbc0,DAT_0049bbbc,DAT_0049bfd8,0x10d,DAT_0049bea8);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_0049bf9c,DAT_0049bf9c);
        }
        uVar1 = 0;
      }
      else {
        *param_2 = local_2c;
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(4,DAT_0049bbc0,DAT_0049bbbc,DAT_0049bfd8,0x112,DAT_0049bfe0,*param_2,
                       *(undefined4 *)(iVar3 + 4));
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_0049bfe4,DAT_0049bfe4,*param_2,
                              *(undefined4 *)(iVar3 + 4));
        }
        uVar1 = 1;
      }
    }
  }
  return uVar1;
}

