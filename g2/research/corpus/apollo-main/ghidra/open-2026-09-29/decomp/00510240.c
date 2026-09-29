
undefined4 CALLBACK_MGR_Register(int *param_1,int param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  if (param_1 == (int *)0x0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00510554,DAT_00510550,DAT_0051057c,100,DAT_0051055c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00510564);
    }
    uVar2 = 0;
  }
  else if (param_2 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00510554,DAT_00510550,DAT_0051057c,0x69,DAT_00510580);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00510584,DAT_00510584);
    }
    uVar2 = 0;
  }
  else {
    iVar1 = callback_mgr_is_registered(param_1,param_2);
    if (iVar1 == 0) {
      iVar1 = CALLBACK_MGR_CreateNode(param_2);
      if (iVar1 == 0) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(1,DAT_00510554,DAT_00510550,DAT_0051057c,0x76,DAT_00510590,param_1[2]);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_00510594,DAT_00510594,param_1[2]);
        }
        uVar2 = 0;
      }
      else {
        *(int *)(iVar1 + 4) = *param_1;
        *param_1 = iVar1;
        *(char *)(param_1 + 1) = (char)param_1[1] + '\x01';
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00510554,DAT_00510550,DAT_0051057c,0x80,DAT_00510598,param_1[2],
                       (char)param_1[1]);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_0051059c,DAT_0051059c,param_1[2],(char)param_1[1]);
        }
        uVar2 = 1;
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,DAT_00510554,DAT_00510550,DAT_0051057c,0x6f,DAT_00510588,param_1[2]);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_0051058c,DAT_0051058c,param_1[2]);
      }
      uVar2 = 1;
    }
  }
  return uVar2;
}

