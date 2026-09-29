
void HciLeRemoveDeviceFromResolvingList(undefined1 param_1,undefined4 param_2)

{
  int iVar1;
  
  iVar1 = hciCmdAlloc(0x2028,7);
  if (iVar1 != 0) {
    *(undefined1 *)(iVar1 + 3) = param_1;
    FUN_004d293c(iVar1 + 4,param_2);
    hciCmdSend(iVar1);
  }
  return;
}

