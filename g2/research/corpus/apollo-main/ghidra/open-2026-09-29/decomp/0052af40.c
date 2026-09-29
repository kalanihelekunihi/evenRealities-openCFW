
undefined4
HciLeConnUpdateCmd(undefined2 param_1,undefined2 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = hciCmdAlloc(0x2013,0xe);
  if (iVar1 != 0) {
    *(char *)(iVar1 + 3) = (char)param_1;
    *(char *)(iVar1 + 4) = (char)((ushort)param_1 >> 8);
    *(char *)(iVar1 + 5) = (char)*param_2;
    *(char *)(iVar1 + 6) = (char)((ushort)*param_2 >> 8);
    *(char *)(iVar1 + 7) = (char)param_2[1];
    *(char *)(iVar1 + 8) = (char)((ushort)param_2[1] >> 8);
    *(char *)(iVar1 + 9) = (char)param_2[2];
    *(char *)(iVar1 + 10) = (char)((ushort)param_2[2] >> 8);
    *(char *)(iVar1 + 0xb) = (char)param_2[3];
    *(char *)(iVar1 + 0xc) = (char)((ushort)param_2[3] >> 8);
    *(char *)(iVar1 + 0xd) = (char)param_2[4];
    *(char *)(iVar1 + 0xe) = (char)((ushort)param_2[4] >> 8);
    *(char *)(iVar1 + 0xf) = (char)param_2[5];
    *(char *)(iVar1 + 0x10) = (char)((ushort)param_2[5] >> 8);
    hciCmdSend(iVar1);
  }
  return param_4;
}

