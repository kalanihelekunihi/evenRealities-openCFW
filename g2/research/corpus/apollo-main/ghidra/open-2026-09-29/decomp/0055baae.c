
undefined4
FUN_0055baae(byte param_1,undefined1 param_2,int param_3,undefined4 param_4,undefined2 param_5,
            undefined2 param_6)

{
  int iVar1;
  byte bVar2;
  byte bVar3;
  
  iVar1 = WsfMsgAlloc(0xe);
  if (iVar1 != 0) {
    *(undefined1 *)(iVar1 + 2) = 0x10;
    *(byte *)(iVar1 + 4) = param_1;
    bVar2 = 0;
    bVar3 = 0;
    while ((bVar2 < 8 && (bVar3 < 2))) {
      if (((uint)param_1 & 1 << (uint)bVar2) != 0) {
        *(undefined1 *)((uint)bVar3 + iVar1 + 5) = *(undefined1 *)(param_3 + (uint)bVar3);
        bVar3 = bVar3 + 1;
      }
      bVar2 = bVar2 + 1;
    }
    *(undefined1 *)(iVar1 + 7) = param_2;
    *(undefined2 *)(iVar1 + 8) = param_5;
    *(undefined2 *)(iVar1 + 10) = param_6;
    *(char *)(iVar1 + 0xc) = (char)param_4;
    WsfMsgSend(*(undefined1 *)(DAT_0055bbc0 + 0xc),iVar1);
  }
  return param_4;
}

