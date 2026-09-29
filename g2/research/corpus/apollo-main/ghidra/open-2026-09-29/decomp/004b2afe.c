
void appSlaveLegAdvStop(int param_1)

{
  int iVar1;
  char cVar2;
  
  if ((*(char *)(param_1 + 2) == 'H') && (*(char *)(param_1 + 4) == '\0')) {
    return;
  }
  if (*(char *)(param_1 + 2) == '\"') {
    cVar2 = FUN_004bac4e(0);
    iVar1 = DAT_004b2dd4;
    if (*DAT_004b2dd0 == '\0') {
      if (cVar2 != '\0') {
        *DAT_004b2dd0 = '\x01';
        iVar1 = DAT_004b2dd4;
        *(undefined1 *)(DAT_004b2dd4 + 10) = 0x22;
        *(undefined2 *)(iVar1 + 8) = 0;
        *(undefined1 *)(iVar1 + 0xc) = *DAT_004b2dd8;
        WsfTimerStartMs(iVar1,100);
        return;
      }
    }
    else {
      if (cVar2 != '\0') {
        *(undefined1 *)(DAT_004b2dd4 + 10) = 0x22;
        *(undefined2 *)(iVar1 + 8) = 0;
        *(undefined1 *)(iVar1 + 0xc) = *DAT_004b2dd8;
        WsfTimerStartMs(iVar1,100);
        return;
      }
      *DAT_004b2dd0 = '\0';
      WsfTimerStop(DAT_004b2dd4);
    }
  }
  if (*(char *)(DAT_004b2dc8 + 0x5b) == '\0') {
    appSlaveNextLegAdvState(param_1);
  }
  else {
    appSlaveLegAdvTypeChanged(param_1);
  }
  return;
}

