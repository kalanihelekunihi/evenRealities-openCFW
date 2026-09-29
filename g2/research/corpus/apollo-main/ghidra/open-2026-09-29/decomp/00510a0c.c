
undefined4 APP_PbRxGlassesCaseFrameDataProcess(int param_1,undefined2 param_2)

{
  char *pcVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 auStack_34 [12];
  int local_28;
  undefined1 auStack_24 [16];
  
  iVar3 = FUN_0043d0ce(0);
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00510f68,DAT_00510f64,DAT_00510f60,0x2f,DAT_00510f5c,param_2);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00510f6c,DAT_00510f6c,param_2);
  }
  pcVar1 = DAT_00510f78;
  if (param_1 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00510f68,DAT_00510f64,DAT_00510f60,0x31,DAT_00510f70);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00510f74,DAT_00510f74);
    }
    uVar4 = 2;
  }
  else {
    FUN_0043c0e4(DAT_00510f78,10,0);
    FUN_0048f49c(auStack_24,param_1,param_2);
    FUN_00439c04(auStack_34,auStack_24,0x10);
    cVar2 = FUN_00490120(auStack_34,DAT_00510f7c,pcVar1);
    if (cVar2 == '\0') {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        iVar3 = DAT_00510f80;
        if (local_28 != 0) {
          iVar3 = local_28;
        }
        FUN_0043d574(1,DAT_00510f68,DAT_00510f64,DAT_00510f60,0x3b,DAT_00510f84,iVar3);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        iVar3 = DAT_00510f80;
        if (local_28 != 0) {
          iVar3 = local_28;
        }
        compress_log_output(0x4400000,DAT_00510f88,DAT_00510f88,iVar3);
      }
      uVar4 = 0x2b;
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00510f68,DAT_00510f64,DAT_00510f60,0x3f,DAT_00510f8c,*pcVar1);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_00510f90,DAT_00510f90,*pcVar1);
      }
      if (*pcVar1 == '\x01') {
        iVar3 = PB_RxGlassesCaseInfo(pcVar1[1],pcVar1 + 4);
        if (iVar3 == 0) {
          uVar4 = APP_PbTxEncodeGlassesCaseInfo(pcVar1[1],pcVar1 + 4);
          return uVar4;
        }
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(2,DAT_00510f68,DAT_00510f64,DAT_00510f60,0x4c,DAT_00510f94,*pcVar1);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x8400000,DAT_00510f98,DAT_00510f98,*pcVar1);
        }
      }
      uVar4 = 1;
    }
  }
  return uVar4;
}

