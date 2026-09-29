
int FUN_004f9f14(char param_1,uint param_2)

{
  ushort *puVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  
  puVar1 = DAT_004fa04c;
  if ((int)param_2 < 1) {
    iVar2 = 0;
  }
  else {
    iVar2 = 0;
    if (param_1 == '\x02') {
      uVar5 = param_2;
      if ((int)(uint)*DAT_004fa04c < (int)param_2) {
        uVar5 = (uint)*DAT_004fa04c;
      }
      for (iVar6 = 0; iVar6 < (int)uVar5; iVar6 = iVar6 + 1) {
        if (*(int *)(DAT_004faa38 + iVar6 * 0x10) != 0) {
          iVar3 = FUN_0043fdda(*(undefined4 *)(DAT_004faa38 + iVar6 * 0x10));
          iVar2 = iVar3 + 4 + iVar2;
        }
      }
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004fa710,DAT_004fa400,DAT_004faa40,0x100c,DAT_004faa3c,param_2,iVar2);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_004fab04,DAT_004fab04,param_2,iVar2);
      }
    }
    else if (param_1 == '\x03') {
      iVar3 = *DAT_004fa04c - param_2;
      iVar6 = iVar3;
      if (iVar3 < 0) {
        iVar3 = 0;
        iVar6 = iVar3;
      }
      for (; iVar3 < (int)(uint)*puVar1; iVar3 = iVar3 + 1) {
        if (*(int *)(DAT_004faa38 + iVar3 * 0x10) != 0) {
          iVar4 = FUN_0043fdda(*(undefined4 *)(DAT_004faa38 + iVar3 * 0x10));
          iVar2 = iVar4 + 4 + iVar2;
        }
      }
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004fa710,DAT_004fa400,DAT_004faa40,0x101c,DAT_004fab08,param_2,iVar6,
                     iVar2);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10c00000,DAT_004fac3c,DAT_004fac3c,param_2,iVar6,iVar2);
      }
    }
  }
  return iVar2;
}

