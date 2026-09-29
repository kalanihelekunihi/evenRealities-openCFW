
undefined8 FUN_0047b59c(undefined1 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  if (param_2 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0x74c;
      FUN_0043d574(1,DAT_0047bc24,DAT_0047bc20,DAT_0047c074,0x74c,DAT_0047c070,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0047c078);
    }
    uVar2 = 0;
  }
  else {
    iVar1 = FUN_0047ad74(param_1);
    if (iVar1 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        param_2 = 0x765;
        FUN_0043d574(4,DAT_0047bc24,DAT_0047bc20,DAT_0047c074,0x765,DAT_0047c154);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_0047c278,DAT_0047c278);
      }
      uVar2 = 0;
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_2 = 0x755;
        FUN_0043d574(4,DAT_0047bc24,DAT_0047bc20,DAT_0047c074,0x755,DAT_0047c07c);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_0047c080,DAT_0047c080);
      }
      FUN_0047a47c(iVar1);
      DmPrivRemDevFromResList(*(undefined1 *)(iVar1 + 6),iVar1,0);
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        param_2 = 0x760;
        FUN_0043d574(4,DAT_0047bc24,DAT_0047bc20,DAT_0047c074,0x760,DAT_0047c14c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_0047c150,DAT_0047c150);
      }
      uVar2 = 1;
    }
  }
  return CONCAT44(param_2,uVar2);
}

