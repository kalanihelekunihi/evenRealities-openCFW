
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_00556a28(char param_1,char param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  bool bVar4;
  
  iVar3 = _DAT_00556cbc;
  if ((*(int *)(_DAT_00556cbc + 0x14) != 0) &&
     (iVar1 = FUN_0044dce2(*(undefined4 *)(_DAT_00556cbc + 0x14),1), iVar1 != 0)) {
    bVar4 = *(char *)(_DAT_005573f8 + 4) == '\0';
    if (param_1 == '\0') {
      if (bVar4) {
        FUN_0058c84e(iVar1);
      }
      FUN_0043dfa4(iVar1,1);
      iVar1 = FUN_0044dce2(*(undefined4 *)(iVar3 + 0x14),2);
      if (iVar1 != 0) {
        FUN_0043ded4(iVar1,1);
      }
      iVar3 = FUN_0044dce2(*(undefined4 *)(iVar3 + 0x14),3);
      if (iVar3 != 0) {
        FUN_0043ded4(iVar3,1);
      }
    }
    else {
      if (bVar4) {
        FUN_0058c836(iVar1);
      }
      FUN_0043ded4(iVar1,1);
      uVar2 = FUN_00556964();
      FUN_0043dfa4(uVar2,1);
      iVar3 = FUN_0044dce2(*(undefined4 *)(iVar3 + 0x14),3);
      if (iVar3 != 0) {
        if (param_2 == '\0') {
          FUN_0043ded4(iVar3,1);
        }
        else {
          FUN_0043dfa4(iVar3,1);
        }
      }
    }
  }
  return param_4;
}

