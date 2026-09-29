
void HciLeAddDeviceToResolvingListCmd
               (undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = hciCmdAlloc(0x2027,0x27);
  if (iVar1 != 0) {
    *(undefined1 *)(iVar1 + 3) = param_1;
    FUN_004d293c(iVar1 + 4,param_2);
    FUN_00439be4(iVar1 + 10,param_3,0x10);
    FUN_00439be4(iVar1 + 0x1a,param_4,0x10);
    hciCmdSend(iVar1);
  }
  return;
}

