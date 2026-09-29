
undefined4 gx8002_uart_async_tick(void)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  char *pcVar4;
  undefined1 auStack_28 [4];
  ushort uStack_24;
  char cStack_21;
  undefined4 uStack_18;
  char cStack_14;
  undefined4 uStack_10;
  int iStack_c;
  
  iVar1 = LvpQueueGet(uRam102083b0,auStack_28);
  if (iVar1 != 0) {
    if ((cStack_21 == '\x01') && (iVar1 = crc32(0,uStack_18,uStack_10), iStack_c != iVar1)) {
      gx8002_printf(uRam102083b4,uStack_10);
    }
    else {
      iVar1 = 0;
      iVar3 = 0x10;
      pcVar4 = pcRam102083b8;
      do {
        if ((*(uint *)(pcVar4 + 4) == (uint)uStack_24) && (*pcVar4 == cStack_14)) {
          uVar2 = (*(code *)(*(uint *)(pcRam102083b8 + iVar1 * 0x1c + 0x14) & 0xfffffffe))
                            (auStack_28,*(undefined4 *)(pcRam102083b8 + iVar1 * 0x1c + 0x18));
          return uVar2;
        }
        iVar1 = iVar1 + 1;
        pcVar4 = pcVar4 + 0x1c;
        iVar3 = iVar3 + -1;
      } while (iVar3 != 0);
    }
  }
  return 0xffffffff;
}

