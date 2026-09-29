
undefined8
dmConnOpenAccept(undefined1 param_1,undefined1 param_2,undefined1 param_3,undefined4 param_4,
                ushort param_5,undefined1 param_6,undefined1 param_7,undefined4 param_8,char param_9
                )

{
  int iVar1;
  ushort *puVar2;
  uint uVar3;
  undefined1 uVar4;
  
  WsfTaskLock(0);
  iVar1 = dmConnCcbByBdAddr(param_8);
  if (iVar1 == 0) {
    iVar1 = dmConnCcbAlloc(param_8);
  }
  WsfTaskUnlock();
  if (iVar1 != 0) {
    puVar2 = (ushort *)WsfMsgAlloc(0x24);
    if (puVar2 != (ushort *)0x0) {
      *puVar2 = (ushort)*(byte *)(iVar1 + 0x10);
      if (param_9 == '\0') {
        uVar4 = 0x18;
      }
      else {
        uVar4 = 0x1a;
      }
      *(undefined1 *)(puVar2 + 1) = uVar4;
      *(undefined1 *)(puVar2 + 2) = param_2;
      *(undefined1 *)((int)puVar2 + 5) = param_3;
      *(char *)(puVar2 + 3) = (char)param_4;
      puVar2[4] = param_5;
      *(undefined1 *)(puVar2 + 5) = param_6;
      FUN_004d293c((int)puVar2 + 0xb,param_8);
      *(undefined1 *)((int)puVar2 + 0x11) = param_7;
      *(undefined1 *)(puVar2 + 9) = param_1;
      WsfMsgSend(*(undefined1 *)(DAT_004b6f20 + 0xc),puVar2);
      WsfTaskLock();
      *(char *)(iVar1 + 0x19) = param_9;
      WsfTaskUnlock();
      uVar3 = (uint)*(byte *)(iVar1 + 0x10);
      goto LAB_004b63c6;
    }
    WsfTaskLock();
    dmConnCcbDealloc(iVar1);
    WsfTaskUnlock();
  }
  uVar3 = 0;
LAB_004b63c6:
  return CONCAT44(param_4,uVar3);
}

