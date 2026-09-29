
undefined4
HciLeRemoteConnParamReqReply
          (undefined2 param_1,undefined2 param_2,undefined4 param_3,undefined4 param_4,
          undefined4 param_5,undefined4 param_6,undefined4 param_7)

{
  int iVar1;
  
  iVar1 = hciCmdAlloc(0x2020,0xe);
  if (iVar1 != 0) {
    *(char *)(iVar1 + 3) = (char)param_1;
    *(char *)(iVar1 + 4) = (char)((ushort)param_1 >> 8);
    *(char *)(iVar1 + 5) = (char)param_2;
    *(char *)(iVar1 + 6) = (char)((ushort)param_2 >> 8);
    *(char *)(iVar1 + 7) = (char)param_3;
    *(char *)(iVar1 + 8) = (char)((uint)param_3 >> 8);
    *(char *)(iVar1 + 9) = (char)param_4;
    *(char *)(iVar1 + 10) = (char)((uint)param_4 >> 8);
    *(char *)(iVar1 + 0xb) = (char)param_5;
    *(char *)(iVar1 + 0xc) = (char)((uint)param_5 >> 8);
    *(char *)(iVar1 + 0xd) = (char)param_6;
    *(char *)(iVar1 + 0xe) = (char)((uint)param_6 >> 8);
    *(char *)(iVar1 + 0xf) = (char)param_7;
    *(char *)(iVar1 + 0x10) = (char)((uint)param_7 >> 8);
    hciCmdSend(iVar1);
  }
  return param_4;
}

