
undefined4 FUN_0047ab6c(undefined1 *param_1,ushort param_2)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = DAT_0047ae64 + (uint)param_2 * 200;
  if (((param_2 < 10) && (*(char *)(iVar3 + 0x2f) != '\0')) && (*(char *)(iVar3 + 0x30) != '\0')) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0047ae28,DAT_0047adcc,DAT_0047b580,0x43b,DAT_0047b588,param_2,param_1[5],
                   param_1[4],param_1[3],param_1[2],param_1[1],*param_1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x11c00000,DAT_0047b58c,DAT_0047b58c,param_2,param_1[5],param_1[4],
                          param_1[3],param_1[2],param_1[1],*param_1);
    }
    if ((int)((uint)*(byte *)(iVar3 + 0x2e) << 0x1f) < 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0047ae28,DAT_0047adcc,DAT_0047b580,0x440,DAT_0047b590);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_0047b594,DAT_0047b594);
      }
      uVar1 = 1;
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0047ae28,DAT_0047adcc,DAT_0047b580,0x449,DAT_0047b598);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_0047b6dc,DAT_0047b6dc);
      }
      uVar1 = 0;
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0047ae28,DAT_0047adcc,DAT_0047b580,0x435,DAT_0047b57c);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0047b584);
    }
    uVar1 = 0;
  }
  return uVar1;
}

