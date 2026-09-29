
void _SetRingLinkState(char param_1,undefined *param_2)

{
  char *pcVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined *puVar5;
  
  pcVar1 = DAT_004a02c8;
  if (param_1 == *DAT_004a02c8) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      puVar5 = param_2;
      if (param_2 == (undefined *)0x0) {
        puVar5 = &DAT_0049fb10;
      }
      uVar3 = _ringLinkStateName(param_1);
      FUN_0043d574(4,DAT_004a02d8,DAT_004a02d4,DAT_004a02d0,0x9c,DAT_004a02cc,uVar3,puVar5);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      if (param_2 == (undefined *)0x0) {
        param_2 = &DAT_0049fb10;
      }
      uVar3 = _ringLinkStateName(param_1);
      compress_log_output(0x10800000,DAT_004a02dc,DAT_004a02dc,uVar3,param_2);
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      puVar5 = param_2;
      if (param_2 == (undefined *)0x0) {
        puVar5 = &DAT_0049fb10;
      }
      uVar3 = _ringLinkStateName(param_1);
      uVar4 = _ringLinkStateName(*pcVar1);
      FUN_0043d574(3,DAT_004a02d8,DAT_004a02d4,DAT_004a02d0,0xa2,DAT_004a02e0,uVar4,uVar3,puVar5);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      if (param_2 == (undefined *)0x0) {
        param_2 = &DAT_0049fb10;
      }
      uVar3 = _ringLinkStateName(param_1);
      uVar4 = _ringLinkStateName(*pcVar1);
      compress_log_output(0xcc00000,DAT_004a0514,DAT_004a0514,uVar4,uVar3,param_2);
    }
    *pcVar1 = param_1;
  }
  return;
}

