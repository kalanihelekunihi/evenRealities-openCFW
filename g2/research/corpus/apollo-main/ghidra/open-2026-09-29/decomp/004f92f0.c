
void FUN_004f92f0(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  for (iVar3 = 0; iVar3 < (int)(uint)*DAT_004f9350; iVar3 = iVar3 + 1) {
    for (iVar4 = 0; iVar1 = DAT_004f9f08, iVar4 < 4; iVar4 = iVar4 + 1) {
      if ((*(int *)(iVar3 * 0x10 + DAT_004f9f08 + iVar4 * 4) != 0) &&
         (iVar2 = FUN_0043e2ea(*(undefined4 *)(iVar3 * 0x10 + DAT_004f9f08 + iVar4 * 4)), iVar2 != 0
         )) {
        FUN_0044d7b8(*(undefined4 *)(iVar3 * 0x10 + iVar1 + iVar4 * 4));
        *(undefined4 *)(iVar3 * 0x10 + iVar1 + iVar4 * 4) = 0;
      }
    }
  }
  return;
}

