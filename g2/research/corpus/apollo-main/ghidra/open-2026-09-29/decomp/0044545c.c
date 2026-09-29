
undefined4
_otaFsHealthCheckAndHeal
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar1 = _otaFsHealthProbe();
  if (iVar1 != 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004455b0,DAT_004455ac,DAT_00445640,0x3ef,DAT_0044563c,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_00445644,DAT_00445644);
    }
    iVar1 = FUN_004761d2();
    if (iVar1 == 0) {
      iVar1 = _otaFsHealthProbe();
      if (iVar1 == 0) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(2,DAT_004455b0,DAT_004455ac,DAT_00445640,0x3fb,DAT_00445658);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_0044565c,DAT_0044565c);
        }
        uVar3 = 0;
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004455b0,DAT_004455ac,DAT_00445640,0x3f8,DAT_00445650);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_00445654,DAT_00445654);
        }
        uVar3 = 0xffffffff;
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004455b0,DAT_004455ac,DAT_00445640,0x3f2,DAT_00445648,iVar1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_0044564c,DAT_0044564c,iVar1);
      }
      uVar3 = 0xffffffff;
    }
    return uVar3;
  }
  return 0;
}

