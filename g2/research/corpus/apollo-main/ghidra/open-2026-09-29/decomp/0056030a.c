
int TouchVerifyApp(void)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  undefined4 in_r3;
  undefined1 local_24 [4];
  undefined1 auStack_20 [16];
  undefined4 uStack_10;
  
  uVar1 = DAT_005608b8;
  local_24[0] = 1;
  uStack_10 = in_r3;
  iVar2 = semantic_TouchBuildAndSendFrame(DAT_005608b8,0x31,local_24,1);
  if (iVar2 == 0) {
    iVar2 = semantic_TouchSendCommandRetry(uVar1,auStack_20,0xf);
    if (iVar2 == 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_005608c8,DAT_005608c4,DAT_00560ea4,0x251,DAT_00560ee8);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_00561078,DAT_00561078);
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_005608c8,DAT_005608c4,DAT_00560ea4,0x24f,DAT_00560ee0,iVar2);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_00560ee4,DAT_00560ee4,iVar2);
      }
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005608c8,DAT_005608c4,DAT_00560ea4,0x249,DAT_00560928,iVar2);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00560edc,DAT_00560edc,iVar2);
    }
  }
  return iVar2;
}

