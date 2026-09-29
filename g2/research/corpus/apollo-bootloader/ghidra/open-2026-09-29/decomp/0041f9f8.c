
void FUN_0041f9f8(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  iVar1 = DAT_0041fa48;
  uVar2 = DAT_0041fa44 - DAT_0041fa40 >> 3;
  if (0x100 < uVar2) {
    uVar2 = 0x100;
  }
  FUN_0041568c(DAT_0041fa48,DAT_0041fa40,uVar2 << 3);
  qsort_public_wrapper(iVar1,uVar2,8,DAT_0041fa4c);
  for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1) {
    if (*(int *)(iVar1 + uVar3 * 8) != 0) {
      (**(code **)(iVar1 + uVar3 * 8))();
    }
  }
  return;
}

