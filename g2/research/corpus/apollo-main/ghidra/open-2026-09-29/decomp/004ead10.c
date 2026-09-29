
void FUN_004ead10(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004eb32c,DAT_004eb328,DAT_004eb750,0x2a0,DAT_004eb74c,param_1,
                 *(undefined1 *)(DAT_004eb740 + 0x124),param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10800000,DAT_004eb754,DAT_004eb754,param_1,
                        *(undefined1 *)(DAT_004eb740 + 0x124));
  }
  piVar1 = DAT_004eb744;
  if (*(char *)(DAT_004eb740 + 0x124) == '\0') {
    if (*DAT_004eb744 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004eb32c,DAT_004eb328,DAT_004eb750,0x2a8,DAT_004eb760);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_004eb764,DAT_004eb764);
      }
    }
    else {
      iVar2 = FUN_0044e498(*DAT_004eb744);
      if (param_1 == 1) {
        iVar3 = FUN_004eac60();
        if (iVar3 == 0) {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(4,DAT_004eb32c,DAT_004eb328,DAT_004eb750,0x2b3,DAT_004eb768);
          }
          iVar2 = FUN_0043d0ce();
          if ((-1 < iVar2 << 0x1f) && (iVar2 = FUN_0043d0ce(), -1 < iVar2 << 0x1d)) {
            return;
          }
          compress_log_output(0x10000000,DAT_004eb76c,DAT_004eb76c);
          return;
        }
        iVar3 = 0x120;
      }
      else {
        iVar3 = FUN_004eacc0();
        if (iVar3 == 0) {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(4,DAT_004eb32c,DAT_004eb328,DAT_004eb750,0x2ba,DAT_004eb770);
          }
          iVar2 = FUN_0043d0ce();
          if ((-1 < iVar2 << 0x1f) && (iVar2 = FUN_0043d0ce(), -1 < iVar2 << 0x1d)) {
            return;
          }
          compress_log_output(0x10000000,DAT_004eb774,DAT_004eb774);
          return;
        }
        iVar3 = -0x120;
      }
      iVar3 = iVar2 + iVar3;
      if (iVar3 < 0) {
        iVar3 = 0;
      }
      else if (0x240 < iVar3) {
        iVar3 = 0x240;
      }
      iVar4 = FUN_0044e4bc(*piVar1);
      if (iVar4 + iVar2 < iVar3) {
        iVar3 = iVar4 + iVar2;
      }
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004eb32c,DAT_004eb328,DAT_004eb750,0x2cb,DAT_004eb778,iVar2,iVar3);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_004eb77c,DAT_004eb77c,iVar2,iVar3);
      }
      FUN_004eb1c0(*piVar1,iVar3,0xfa);
      if (param_1 == 1) {
        *DAT_004eb748 = *DAT_004eb748 + 1;
      }
      else {
        *DAT_004eb748 = *DAT_004eb748 + -1;
      }
      if (*DAT_004eb748 < 0) {
        *DAT_004eb748 = 0;
      }
      else if (2 < *DAT_004eb748) {
        *DAT_004eb748 = 2;
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004eb32c,DAT_004eb328,DAT_004eb750,0x2a3,DAT_004eb758);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004eb75c);
    }
  }
  return;
}

