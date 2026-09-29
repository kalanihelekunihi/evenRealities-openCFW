
int FUN_004f6d84(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = param_2;
  if (param_1 != 0) {
    iVar1 = FUN_0044e498(param_1);
    iVar2 = FUN_0044e4bc(param_1);
    iVar2 = iVar2 + iVar1;
    if (param_2 < 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004f758c,DAT_004f7588,DAT_004f78c0,0x74c,DAT_004f785c,param_2,0,param_4);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_004f78c4,DAT_004f78c4,param_2,0);
      }
      iVar3 = 0;
    }
    else if (iVar2 < param_2) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004f758c,DAT_004f7588,DAT_004f78c0,0x750,DAT_004f78c8,param_2,iVar2,
                     param_4);
      }
      iVar1 = FUN_0043d0ce();
      iVar3 = iVar2;
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_004f7adc,DAT_004f7adc,param_2,iVar2);
      }
    }
  }
  return iVar3;
}

