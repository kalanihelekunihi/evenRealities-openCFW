
void HciLeSetAdvParamCmd(undefined2 param_1,undefined2 param_2,undefined1 param_3,undefined1 param_4
                        ,undefined1 param_5,int param_6,undefined1 param_7,undefined1 param_8)

{
  int iVar1;
  undefined1 *puVar2;
  
  iVar1 = hciCmdAlloc(0x2006,0xf);
  if (iVar1 != 0) {
    *(char *)(iVar1 + 3) = (char)param_1;
    *(char *)(iVar1 + 4) = (char)((ushort)param_1 >> 8);
    *(char *)(iVar1 + 5) = (char)param_2;
    *(char *)(iVar1 + 6) = (char)((ushort)param_2 >> 8);
    *(undefined1 *)(iVar1 + 7) = param_3;
    *(undefined1 *)(iVar1 + 8) = param_4;
    *(undefined1 *)(iVar1 + 9) = param_5;
    if (param_6 == 0) {
      puVar2 = (undefined1 *)FUN_004d2960(iVar1 + 10);
    }
    else {
      FUN_004d293c(iVar1 + 10);
      puVar2 = (undefined1 *)(iVar1 + 0x10);
    }
    *puVar2 = param_7;
    puVar2[1] = param_8;
    hciCmdSend(iVar1);
  }
  return;
}

