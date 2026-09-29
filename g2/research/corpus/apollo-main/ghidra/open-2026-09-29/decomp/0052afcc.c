
void HciLeCreateConnCmd(undefined2 param_1,undefined2 param_2,undefined1 param_3,undefined1 param_4,
                       undefined4 param_5,undefined1 param_6,undefined2 *param_7)

{
  int iVar1;
  
  iVar1 = hciCmdAlloc(0x200d,0x19);
  if (iVar1 != 0) {
    *(char *)(iVar1 + 3) = (char)param_1;
    *(char *)(iVar1 + 4) = (char)((ushort)param_1 >> 8);
    *(char *)(iVar1 + 5) = (char)param_2;
    *(char *)(iVar1 + 6) = (char)((ushort)param_2 >> 8);
    *(undefined1 *)(iVar1 + 7) = param_3;
    *(undefined1 *)(iVar1 + 8) = param_4;
    FUN_004d293c(iVar1 + 9,param_5);
    *(undefined1 *)(iVar1 + 0xf) = param_6;
    *(char *)(iVar1 + 0x10) = (char)*param_7;
    *(char *)(iVar1 + 0x11) = (char)((ushort)*param_7 >> 8);
    *(char *)(iVar1 + 0x12) = (char)param_7[1];
    *(char *)(iVar1 + 0x13) = (char)((ushort)param_7[1] >> 8);
    *(char *)(iVar1 + 0x14) = (char)param_7[2];
    *(char *)(iVar1 + 0x15) = (char)((ushort)param_7[2] >> 8);
    *(char *)(iVar1 + 0x16) = (char)param_7[3];
    *(char *)(iVar1 + 0x17) = (char)((ushort)param_7[3] >> 8);
    *(char *)(iVar1 + 0x18) = (char)param_7[4];
    *(char *)(iVar1 + 0x19) = (char)((ushort)param_7[4] >> 8);
    *(char *)(iVar1 + 0x1a) = (char)param_7[5];
    *(char *)(iVar1 + 0x1b) = (char)((ushort)param_7[5] >> 8);
    hciCmdSend(iVar1);
  }
  return;
}

