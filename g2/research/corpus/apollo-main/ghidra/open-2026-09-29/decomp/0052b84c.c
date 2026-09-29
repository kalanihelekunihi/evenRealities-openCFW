
undefined4
HciVendorSpecificCmd(undefined2 param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = hciCmdAlloc(param_1,param_2);
  if (iVar1 != 0) {
    FUN_00439be4(iVar1 + 3,param_3,param_2);
    hciCmdSend(iVar1);
  }
  return param_4;
}

