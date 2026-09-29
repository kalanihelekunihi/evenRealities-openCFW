
int FUN_0058c89e(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  code *pcVar4;
  
  if (param_1 < 10) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar2 = FUN_0058c892(param_1);
      FUN_0043d574(3,DAT_0058d2dc,DAT_0058d2d8,DAT_0058d2d4,100,DAT_0058d2e4,param_1,uVar2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      uVar2 = FUN_0058c892(param_1);
      compress_log_output(0xc800000,DAT_0058d2e8,DAT_0058d2e8,param_1,uVar2);
    }
    pcVar4 = *(code **)(DAT_0058d2ec + (uint)param_1 * 4);
    if (pcVar4 == (code *)0x0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar2 = FUN_0058c892(param_1);
        FUN_0043d574(2,DAT_0058d2dc,DAT_0058d2d8,DAT_0058d2d4,0x6b,DAT_0058d2f0,param_1,uVar2);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        uVar2 = FUN_0058c892(param_1);
        compress_log_output(0x8800000,DAT_0058d418,DAT_0058d418,param_1,uVar2);
      }
      iVar1 = -1;
    }
    else {
      iVar1 = (*pcVar4)(DAT_0058d410,param_2,param_3);
      if (iVar1 != 0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(2,DAT_0058d2dc,DAT_0058d2d8,DAT_0058d2d4,0x72,DAT_0058d41c);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_0058d420,DAT_0058d420);
        }
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0058d2dc,DAT_0058d2d8,DAT_0058d2d4,0x60,DAT_0058d2d0,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0058d2e0,DAT_0058d2e0);
    }
    iVar1 = -1;
  }
  return iVar1;
}

