
void FUN_005b873c(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined1 auStack_28 [16];
  
  if ((((param_1 != 0) && (*(int *)(param_1 + 4) != 0)) &&
      (iVar1 = FUN_0043e2ea(*(undefined4 *)(param_1 + 4)), iVar1 != 0)) &&
     (iVar1 = FUN_005b8a6a(*(undefined1 *)(param_1 + 8)), -1 < iVar1)) {
    health_lock_storage();
    uVar3 = *(undefined4 *)(iVar1 * 0x18 + DAT_005b89e8 + 0xc);
    uVar2 = *(undefined4 *)(DAT_005b89e8 + iVar1 * 0x18 + 0x14);
    health_unlock_storage();
    FUN_0043c0e4(auStack_28,0x10,0);
    FUN_005b8a9c(uVar3,*(undefined1 *)(param_1 + 8),uVar2,auStack_28,0x10);
    FUN_0049942e(*(undefined4 *)(param_1 + 4),auStack_28);
    FUN_005b7a4c(param_1);
  }
  return;
}

