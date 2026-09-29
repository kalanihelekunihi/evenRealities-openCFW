
int FUN_005b4904(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  code *pcVar4;
  
  if (param_1 < 0xd) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar2 = FUN_005b48f8(param_1);
      FUN_0043d574(3,DAT_005b52d8,DAT_005b52d4,DAT_005b52d0,0x5d,DAT_005b53fc,param_1,uVar2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      uVar2 = FUN_005b48f8(param_1);
      compress_log_output(0xc800000,DAT_005b5400,DAT_005b5400,param_1,uVar2);
    }
    pcVar4 = *(code **)(DAT_005b5404 + (uint)param_1 * 4);
    if (pcVar4 == (code *)0x0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar2 = FUN_005b48f8(param_1);
        FUN_0043d574(2,DAT_005b52d8,DAT_005b52d4,DAT_005b52d0,100,DAT_005b5408,param_1,uVar2);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        uVar2 = FUN_005b48f8(param_1);
        compress_log_output(0x8800000,DAT_005b540c,DAT_005b540c,param_1,uVar2);
      }
      iVar1 = -1;
    }
    else {
      iVar1 = (*pcVar4)(DAT_005b5410,param_2,param_3);
      if (iVar1 != 0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(2,DAT_005b52d8,DAT_005b52d4,DAT_005b52d0,0x6b,DAT_005b5414);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_005b5630,DAT_005b5630);
        }
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005b52d8,DAT_005b52d4,DAT_005b52d0,0x59,DAT_005b52cc,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005b52dc,DAT_005b52dc);
    }
    iVar1 = -1;
  }
  return iVar1;
}

