
undefined4 FUN_1000b430(undefined1 *param_1)

{
  undefined1 *puVar1;
  int iVar2;
  int iVar3;
  undefined1 *puVar4;
  int *piVar5;
  
  puVar1 = DAT_1000b4c0;
  iVar2 = 0x10;
  puVar4 = DAT_1000b4c0;
  do {
    if (*(int *)(param_1 + 4) == *(int *)(puVar4 + 4)) {
      *(undefined4 *)(puVar4 + 4) = 0;
      *puVar4 = 0xff;
      *(undefined4 *)(puVar4 + 8) = 0;
      *(undefined4 *)(puVar4 + 0xc) = 0;
      *(undefined4 *)(puVar4 + 0x10) = 0;
      *(undefined4 *)(puVar4 + 0x18) = 0;
      *(undefined4 *)(puVar4 + 0x14) = 0;
    }
    puVar4 = puVar4 + 0x1c;
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  iVar2 = 0;
  if (*(int *)(puVar1 + 4) != 0) {
    iVar2 = 1;
    iVar3 = 0xf;
    piVar5 = DAT_1000b4c4;
    while (*piVar5 != 0) {
      iVar2 = iVar2 + 1;
      piVar5 = piVar5 + 7;
      iVar3 = iVar3 + -1;
      if (iVar3 == 0) {
        return 0xffffffff;
      }
    }
  }
  iVar2 = iVar2 * 0x1c;
  *(undefined4 *)(puVar1 + iVar2 + 4) = *(undefined4 *)(param_1 + 4);
  puVar1[iVar2] = *param_1;
  *(undefined4 *)(puVar1 + iVar2 + 8) = *(undefined4 *)(param_1 + 8);
  *(undefined4 *)(puVar1 + iVar2 + 0xc) = *(undefined4 *)(param_1 + 0xc);
  *(undefined4 *)(puVar1 + iVar2 + 0x10) = *(undefined4 *)(param_1 + 0x10);
  *(undefined4 *)(puVar1 + iVar2 + 0x18) = *(undefined4 *)(param_1 + 0x18);
  *(undefined4 *)(puVar1 + iVar2 + 0x14) = *(undefined4 *)(param_1 + 0x14);
  return 0;
}

