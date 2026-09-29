
void dmConnReset(void)

{
  int iVar1;
  undefined4 in_r3;
  byte bVar2;
  int iVar3;
  char cVar4;
  undefined2 uStack_a0;
  undefined1 uStack_9e;
  undefined1 uStack_9d;
  undefined1 uStack_9c;
  undefined2 uStack_9a;
  undefined1 uStack_98;
  undefined4 uStack_18;
  
  iVar1 = DAT_004b71d4;
  uStack_9c = 0;
  uStack_9d = 0;
  uStack_98 = 0x16;
  iVar3 = DAT_004b71d4;
  uStack_18 = in_r3;
  for (cVar4 = '\x03'; cVar4 != '\0'; cVar4 = cVar4 + -1) {
    if (*(char *)(iVar3 + 0x16) != '\0') {
      uStack_a0 = *(undefined2 *)(iVar3 + 0xc);
      uStack_9e = 3;
      uStack_9a = uStack_a0;
      dmConnHciHandler(&uStack_a0);
    }
    iVar3 = iVar3 + 0x30;
  }
  for (bVar2 = 0; iVar3 = DAT_004b6f20, bVar2 < 2; bVar2 = bVar2 + 1) {
    *(undefined2 *)(iVar1 + (uint)bVar2 * 2 + 0xbc) = 0x60;
    *(undefined2 *)(iVar1 + (uint)bVar2 * 2 + 0xc0) = 0x30;
    FUN_00439be4(iVar1 + (uint)bVar2 * 0xc + 0xa4,DAT_004b71d8,0xc);
  }
  *(undefined1 *)(DAT_004b6f20 + 0x14) = 0;
  *(undefined1 *)(iVar3 + 0xd) = 0;
  return;
}

