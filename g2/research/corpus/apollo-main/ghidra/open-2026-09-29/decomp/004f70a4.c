
void FUN_004f70a4(undefined4 param_1)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int local_24;
  int local_20;
  undefined1 auStack_1c [4];
  undefined1 auStack_18 [4];
  
  piVar1 = DAT_004f747c;
  if (*DAT_004f747c != 0) {
    FUN_004f6fc4(param_1,auStack_18,&local_24,auStack_1c,&local_20);
    iVar2 = FUN_0043fdda(*piVar1);
    iVar3 = FUN_0044e498(*piVar1);
    iVar4 = local_24;
    if ((-1 < local_24 - iVar3) && (iVar4 = iVar3, iVar2 < local_20 + (local_24 - iVar3))) {
      iVar4 = (local_20 + local_24) - iVar2;
    }
    iVar4 = FUN_004f6d84(*piVar1,iVar4);
    if (iVar4 != iVar3) {
      FUN_0044ea04(*piVar1,iVar4,0);
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004f758c,DAT_004f7588,DAT_004f7b80,0x7e3,DAT_004f7b7c,param_1,iVar3,iVar4
                    );
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10c00000,DAT_004f7c8c,DAT_004f7c8c,param_1,iVar3,iVar4);
      }
    }
  }
  return;
}

