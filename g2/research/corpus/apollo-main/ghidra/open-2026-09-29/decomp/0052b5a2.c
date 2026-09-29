
undefined4
HciLeStartEncryptionCmd(undefined2 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = hciCmdAlloc(0x2019,0x1c);
  if (iVar1 != 0) {
    *(char *)(iVar1 + 3) = (char)param_1;
    *(char *)(iVar1 + 4) = (char)((ushort)param_1 >> 8);
    FUN_00439be4(iVar1 + 5,param_2,8);
    *(char *)(iVar1 + 0xd) = (char)param_3;
    *(char *)(iVar1 + 0xe) = (char)((uint)param_3 >> 8);
    FUN_00439be4(iVar1 + 0xf,param_4,0x10);
    hciCmdSend(iVar1);
  }
  return param_4;
}

