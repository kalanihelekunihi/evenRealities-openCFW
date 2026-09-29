
void FUN_10004a48(uint param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  int local_28 [2];
  uint *puStack_20;
  int *piStack_18;
  int *piStack_14;
  
  if (param_1 - 7 < 0x12) {
                    /* WARNING: Could not recover jumptable at 0x10004a5c. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (*(code *)(*(uint *)(PTR_PTR_10004a60 + (param_1 - 7) * 4) & 0xfffffffe))();
    return;
  }
  iVar1 = FUN_1000452c(param_1,local_28);
  if (iVar1 != 0) goto LAB_10004ab0;
  uVar2 = (uint)*(char *)(local_28[0] + 6);
  if (uVar2 == 0xffffffff) goto LAB_10004ab0;
  if ((param_1 < 10) && ((1 << (param_1 & 0x3f) & 0x243U) != 0)) {
    uVar3 = *puStack_20;
    if ((uVar3 >> (uVar2 + 1 & 0x3f) & 1) == 0) goto LAB_10004ae8;
  }
  else {
    uVar3 = *puStack_20;
LAB_10004ae8:
    if (((uVar3 >> (uVar2 & 0x3f) & 1) != 0) && (param_2 != 0)) {
      *piStack_14 = 1 << ((int)*(char *)(local_28[0] + 4) & 0x3fU);
      goto LAB_10004ab0;
    }
  }
  *piStack_18 = 1 << ((int)*(char *)(local_28[0] + 4) & 0x3fU);
LAB_10004ab0:
  iVar1 = FUN_1000452c(param_1,local_28);
  if (iVar1 == 0) {
    iVar1 = 1 << ((int)*(char *)(local_28[0] + 5) & 0x3fU);
    if (param_1 - 6 < 0x13) {
                    /* WARNING: Could not recover jumptable at 0x10004ad2. Too many branches */
                    /* WARNING: Treating indirect jump as call */
      (*(code *)(*(uint *)(PTR_PTR_10004ad4 + (param_1 - 6) * 4) & 0xfffffffe))();
      return;
    }
    if (((param_1 & 0xfffffffb) != 1) && (iVar1 != 0)) {
      if (param_2 != 0) {
        *piStack_14 = iVar1;
        return;
      }
      *piStack_18 = iVar1;
    }
  }
  return;
}

