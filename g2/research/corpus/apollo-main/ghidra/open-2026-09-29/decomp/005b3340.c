
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_005b3340(int param_1)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  if (((param_1 != 0) && (iVar1 = FUN_0043e2ea(param_1), iVar1 != 0)) &&
     (param_1 != *(int *)(_DAT_005b3514 + 0x18))) {
    FUN_00450500(param_1,0);
    uVar2 = FUN_0044ddea(param_1);
    for (uVar3 = 0; uVar3 < uVar2; uVar3 = uVar3 + 1) {
      FUN_0044dce2(param_1,uVar3);
      FUN_005b3340();
    }
  }
  return;
}

