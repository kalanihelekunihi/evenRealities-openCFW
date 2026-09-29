
int TouchEnterDFU(void)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  undefined4 in_r3;
  undefined4 local_24;
  undefined1 auStack_20 [16];
  undefined4 uStack_10;
  
  uVar1 = DAT_005608b8;
  local_24 = *DAT_005608b4;
  uStack_10 = in_r3;
  iVar2 = semantic_TouchBuildAndSendFrame(DAT_005608b8,0x38,&local_24,4);
  if (iVar2 == 0) {
    iVar2 = semantic_TouchSendCommandRetry(uVar1,auStack_20,0xf);
    if (iVar2 == 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_005608c8,DAT_005608c4,DAT_005608c0,0x1f5,DAT_005608d8,0);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_005608dc,DAT_005608dc,0);
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_005608c8,DAT_005608c4,DAT_005608c0,499,DAT_005608d0,iVar2);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_005608d4,DAT_005608d4,iVar2);
      }
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005608c8,DAT_005608c4,DAT_005608c0,0x1ed,DAT_005608bc,iVar2);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_005608cc,DAT_005608cc,iVar2);
    }
  }
  return iVar2;
}

