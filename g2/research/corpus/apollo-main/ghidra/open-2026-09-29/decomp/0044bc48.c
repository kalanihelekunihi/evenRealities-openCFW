
void FUN_0044bc48(undefined4 param_1)

{
  int iVar1;
  uint uVar2;
  
  if (*(char *)(DAT_0044c154 + 0x24) != '\0') {
    for (iVar1 = FUN_0044fa22(0); iVar1 != 0; iVar1 = FUN_0044fa22(iVar1)) {
      for (uVar2 = 0; uVar2 < *(uint *)(iVar1 + 0x2d4); uVar2 = uVar2 + 1) {
        FUN_0044c970(param_1,*(undefined4 *)(*(int *)(iVar1 + 0x2b8) + uVar2 * 4));
      }
    }
  }
  return;
}

