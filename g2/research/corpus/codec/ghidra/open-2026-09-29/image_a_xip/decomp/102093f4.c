
undefined4 gx8002_app_reply(int param_1,ushort param_2,undefined2 param_3)

{
  int iVar1;
  int iVar2;
  
  *(undefined2 *)(DAT_10209424 + 0x24) = param_3;
  iVar1 = DAT_10209428;
  if (param_1 == 1) {
    param_2 = param_2 | 0x300;
  }
  else {
    param_2 = param_2 | 0x200;
  }
  *(undefined1 *)(DAT_10209428 + 7) = 1;
  *(undefined4 *)(iVar1 + 0x10) = DAT_1020942c;
  iVar2 = DAT_10209428;
  *(ushort *)(iVar1 + 4) = param_2;
  *(undefined4 *)(iVar1 + 0x18) = 2;
  UartMessageAsyncSend(iVar2);
  return 0;
}

