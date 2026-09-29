
undefined1 * smpScCatResponderBdAddr(int param_1,undefined1 *param_2)

{
  int iVar1;
  int iVar2;
  
  iVar1 = dmConnCcbById(*(undefined1 *)(param_1 + 0x3d));
  if (iVar1 != 0) {
    if (*(char *)(param_1 + 0x3a) == '\0') {
      iVar2 = FUN_004d2974(iVar1 + 0x1a);
      if (iVar2 == 0) {
        *param_2 = 1;
        WStrReverseCpy(param_2 + 1,iVar1 + 0x1a,6);
      }
      else {
        *param_2 = *(undefined1 *)(iVar1 + 0x14);
        WStrReverseCpy(param_2 + 1,iVar1 + 6,6);
      }
    }
    else {
      iVar2 = FUN_004d2974(iVar1 + 0x20);
      if (iVar2 == 0) {
        *param_2 = 1;
        WStrReverseCpy(param_2 + 1,iVar1 + 0x20,6);
      }
      else {
        *param_2 = *(undefined1 *)(iVar1 + 0x13);
        WStrReverseCpy(param_2 + 1,iVar1,6);
      }
    }
    param_2 = param_2 + 7;
  }
  return param_2;
}

