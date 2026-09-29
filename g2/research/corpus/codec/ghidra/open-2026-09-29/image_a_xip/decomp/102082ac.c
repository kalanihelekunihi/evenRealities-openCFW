
undefined4 UartMessageAsyncRegist(undefined1 *param_1)

{
  undefined1 *puVar1;
  int iVar2;
  undefined1 *puVar3;
  int iVar4;
  int iVar5;
  
  puVar1 = puRam10208330;
  iVar4 = 0x11;
  puVar3 = puRam10208330;
  while (iVar4 = iVar4 + -1, iVar4 != 0) {
    if (*(int *)(param_1 + 4) == *(int *)(puVar3 + 4)) {
      *(undefined4 *)(puVar3 + 4) = 0;
      *puVar3 = 0xff;
      *(undefined4 *)(puVar3 + 8) = 0;
      *(undefined4 *)(puVar3 + 0xc) = 0;
      *(undefined4 *)(puVar3 + 0x10) = 0;
      *(undefined4 *)(puVar3 + 0x18) = 0;
      *(undefined4 *)(puVar3 + 0x14) = 0;
    }
    puVar3 = puVar3 + 0x1c;
  }
  iVar2 = 0x10;
  iVar4 = 0;
  iVar5 = 0;
  do {
    if (*(int *)(puVar1 + iVar5 + 4) == 0) {
      iVar4 = iVar4 * 0x1c;
      *(undefined4 *)(puVar1 + iVar4 + 4) = *(undefined4 *)(param_1 + 4);
      puVar1[iVar4] = *param_1;
      *(undefined4 *)(puVar1 + iVar4 + 8) = *(undefined4 *)(param_1 + 8);
      *(undefined4 *)(puVar1 + iVar4 + 0xc) = *(undefined4 *)(param_1 + 0xc);
      *(undefined4 *)(puVar1 + iVar4 + 0x10) = *(undefined4 *)(param_1 + 0x10);
      *(undefined4 *)(puVar1 + iVar4 + 0x18) = *(undefined4 *)(param_1 + 0x18);
      *(undefined4 *)(puVar1 + iVar4 + 0x14) = *(undefined4 *)(param_1 + 0x14);
      return 0;
    }
    iVar4 = iVar4 + 1;
    iVar2 = iVar2 + -1;
    iVar5 = iVar5 + 0x1c;
  } while (iVar2 != 0);
  return 0xffffffff;
}

