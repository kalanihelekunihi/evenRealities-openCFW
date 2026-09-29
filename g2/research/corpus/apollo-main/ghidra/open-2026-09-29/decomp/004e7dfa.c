
void FUN_004e7dfa(int param_1)

{
  int *piVar1;
  int *piVar2;
  int *piVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  
  piVar3 = DAT_004e8454;
  piVar2 = DAT_004e83bc;
  piVar1 = DAT_004e7ff4;
  if (*DAT_004e8454 != 0) {
    if (*DAT_004e83bc == 0) {
      if ((param_1 < 0) || (*DAT_004e80dc + -1 < param_1)) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(2,DAT_004e7fe8,DAT_004e7fe4,DAT_004e84a8,0x259,DAT_004e895c,param_1);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x8400000,DAT_004e8960,DAT_004e8960,param_1);
        }
      }
      else if (param_1 == *DAT_004e7ff4) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004e7fe8,DAT_004e7fe4,DAT_004e84a8,0x25f,DAT_004e8964,param_1);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xc400000,DAT_004e8968,DAT_004e8968,param_1);
        }
      }
      else {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004e7fe8,DAT_004e7fe4,DAT_004e84a8,0x263,DAT_004e896c,*piVar1,param_1);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_004e8a60,DAT_004e8a60,*piVar1,param_1);
        }
        iVar5 = param_1 * 0x130;
        iVar4 = FUN_00509694(param_1 - *piVar1);
        iVar6 = (iVar4 + -1) * 0x32 + *DAT_004e83b8;
        *piVar1 = param_1;
        *piVar2 = 1;
        FUN_004e7cc0(*piVar3,iVar5,iVar6);
        FUN_004e772c(*piVar1);
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004e7fe8,DAT_004e7fe4,DAT_004e84a8,0x279,DAT_004e8a64,iVar5,iVar6);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_004e8bb4,DAT_004e8bb4,iVar5,iVar6);
        }
      }
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(3,DAT_004e7fe8,DAT_004e7fe4,DAT_004e84a8,0x253,DAT_004e84a4,*piVar2);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_004e84ac,DAT_004e84ac,*piVar2);
      }
    }
  }
  return;
}

