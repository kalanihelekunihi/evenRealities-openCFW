
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_0043c496(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  byte *pbVar1;
  int *piVar2;
  int iVar3;
  undefined4 uVar4;
  byte bVar5;
  
  pbVar1 = _DAT_0043c784;
  if (param_1 == 2) {
    uVar4 = param_4;
    iVar3 = FUN_0043d0ce();
    bVar5 = (byte)(param_2 >> 0x18);
    if (iVar3 << 0x1e < 0) {
      bVar5 = 0;
      FUN_0043d574(4,DAT_0043c764,DAT_0043c760,_DAT_0043c77c,0x41,_DAT_0043c778,uVar4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,_DAT_0043c780,_DAT_0043c780);
    }
    *_DAT_0043c784 = 0;
    piVar2 = _DAT_0043c788;
    if (*_DAT_0043c788 != 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        bVar5 = 0;
        FUN_0043d574(4,DAT_0043c764,DAT_0043c760,_DAT_0043c77c,0x47,_DAT_0043c78c);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,_DAT_0043c790);
      }
      *piVar2 = 0;
      *_DAT_0043c794 = 0;
      *_DAT_0043c798 = 0;
    }
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      bVar5 = 0;
      FUN_0043d574(4,DAT_0043c764,DAT_0043c760,_DAT_0043c77c,0x4d,_DAT_0043c79c);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,_DAT_0043c7a0,_DAT_0043c7a0);
    }
    iVar3 = FUN_0043de82(param_4);
    *piVar2 = iVar3;
    FUN_0043dfa4(*piVar2,0x10);
    FUN_0043f506(*piVar2,0x240);
    FUN_0043f568(*piVar2,0x120);
    FUN_0043dfa4(*piVar2,0x10);
    uVar4 = FUN_0044104c(0);
    FUN_0044127e(*piVar2,uVar4,0);
    FUN_0044129e(*piVar2,0xff,0);
    param_2 = (uint)bVar5 << 0x18;
    FUN_004412ec(*piVar2,param_2,0);
    FUN_0043c5f6();
    *(int *)(_DAT_0043c7a4 + 4) = *piVar2;
  }
  else if (param_1 == 3) {
    *_DAT_0043c784 = *_DAT_0043c784 + 1;
    if (5 < *pbVar1) {
      *pbVar1 = 0;
    }
    FUN_0043c6ce();
  }
  return (ulonglong)param_2 << 0x20;
}

