
void smpResumeAttemptsState(undefined1 param_1)

{
  undefined1 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar2 = smpCcbByConnId(param_1);
  iVar3 = SmpDbGetPairingDisabledTime(param_1);
  if (iVar3 != 0) {
    if (*(char *)(DAT_00537ebc + 0xf8) == '\0') {
      iVar4 = DmConnRole(param_1);
      if (iVar4 == 1) {
        uVar1 = 0xd;
      }
      else {
        uVar1 = 0xc;
      }
      *(undefined1 *)(iVar2 + 0x3e) = uVar1;
    }
    else {
      iVar4 = DmConnRole(param_1);
      if (iVar4 == 1) {
        uVar1 = 0x26;
      }
      else {
        uVar1 = 0x24;
      }
      *(undefined1 *)(iVar2 + 0x3e) = uVar1;
    }
    *(undefined1 *)(iVar2 + 0x1a) = 0x10;
    WsfTimerStartMs(iVar2 + 0x10,iVar3);
  }
  return;
}

