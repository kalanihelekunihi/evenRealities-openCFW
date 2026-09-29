
/* WARNING: Removing unreachable block (ram,0x005ce2bc) */
/* WARNING: Removing unreachable block (ram,0x005ce2c6) */
/* WARNING: Removing unreachable block (ram,0x005ce2c2) */
/* WARNING: Removing unreachable block (ram,0x005ce2ca) */

undefined4 APP_PbRxRingFrameDataProcess(int param_1,undefined2 param_2)

{
  char *pcVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 unaff_r11;
  undefined4 unaff_pc;
  undefined1 auStack_34 [12];
  int local_28;
  undefined1 auStack_24 [16];
  
  iVar3 = FUN_0043d0ce(0);
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(4,DAT_005ce73c,DAT_005ce738,DAT_005ce734,0x31,DAT_005ce730,param_2);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_005ce740,DAT_005ce740,param_2);
  }
  pcVar1 = DAT_005ce74c;
  if (param_1 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005ce73c,DAT_005ce738,DAT_005ce734,0x33,DAT_005ce744);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005ce748,DAT_005ce748);
    }
    uVar4 = 2;
  }
  else {
    FUN_0043c0e4(DAT_005ce74c,0x40,0);
    FUN_0048f49c(auStack_24,param_1,param_2);
    FUN_00439c04(auStack_34,auStack_24,0x10);
    cVar2 = FUN_00490120(auStack_34,DAT_005ce750,pcVar1);
    if (cVar2 == '\0') {
      createPAC(0x5ce2af,unaff_r11,unaff_pc,0);
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        iVar3 = DAT_005ce754;
        if (local_28 != 0) {
          iVar3 = local_28;
        }
        compress_log_output(0x4400000,DAT_005ce75c,DAT_005ce75c,iVar3);
      }
      uVar4 = 0x2b;
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_005ce73c,DAT_005ce738,DAT_005ce734,0x41,DAT_005ce760,*pcVar1);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_005ce764,DAT_005ce764,*pcVar1);
      }
      if (*pcVar1 == '\x01') {
        iVar3 = PB_RxRingEvent(pcVar1[1],pcVar1 + 4);
        if (iVar3 == 0) {
          uVar4 = APP_PbTxEncodeRingEvent(pcVar1[1],pcVar1 + 4);
          return uVar4;
        }
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(2,DAT_005ce73c,DAT_005ce738,DAT_005ce734,0x4e,DAT_005ce768,*pcVar1);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x8400000,DAT_005ce76c,DAT_005ce76c,*pcVar1);
        }
      }
      uVar4 = 1;
    }
  }
  return uVar4;
}

