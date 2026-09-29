
int TouchProgramData(int param_1,undefined4 param_2)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int local_24;
  undefined4 local_20;
  undefined1 auStack_1c [16];
  
  uVar1 = DAT_005608b8;
  local_24 = param_1 + 0x3300;
  local_20 = param_2;
  iVar2 = semantic_TouchBuildAndSendFrame(DAT_005608b8,0x49,&local_24,8);
  if (iVar2 == 0) {
    iVar2 = semantic_TouchSendCommandRetry(uVar1,auStack_1c,0xf);
    if (iVar2 != 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_005608c8,DAT_005608c4,DAT_0056091c,0x23d,DAT_00560924,iVar2);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_00560ed8,DAT_00560ed8,iVar2);
      }
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005608c8,DAT_005608c4,DAT_0056091c,0x237,DAT_00560918,iVar2);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00560920,DAT_00560920,iVar2);
    }
  }
  return iVar2;
}

