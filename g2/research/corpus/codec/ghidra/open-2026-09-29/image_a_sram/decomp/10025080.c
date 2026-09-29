
void gx8002_platform_gate(uint param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  int *piVar4;
  int local_28 [2];
  uint *puStack_20;
  int *piStack_18;
  int *piStack_14;
  
  if (param_1 - 7 < 0x12) {
                    /* WARNING: Could not recover jumptable at 0x10025094. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (*(code *)(*(uint *)(PTR_PTR_10025098 + (param_1 - 7) * 4) & 0xfffffffe))();
    return;
  }
  iVar1 = __module_get_info(param_1,local_28);
  if ((iVar1 == 0) && (uVar3 = (uint)*(char *)(local_28[0] + 6), uVar3 != 0xffffffff)) {
    uVar2 = 0;
    if ((param_1 < 10) && (uVar2 = 0, (1 << (param_1 & 0x3f) & 0x243U) != 0)) {
      uVar2 = uVar3 + 1;
    }
    piVar4 = piStack_18;
    if ((((uVar2 == 0) || ((*puStack_20 >> (uVar2 & 0x3f) & 1) == 0)) &&
        ((*puStack_20 >> (uVar3 & 0x3f) & 1) != 0)) && (param_2 != 0)) {
      piVar4 = piStack_14;
    }
    *piVar4 = 1 << ((int)*(char *)(local_28[0] + 4) & 0x3fU);
  }
  iVar1 = __module_get_info(param_1,local_28);
  if (iVar1 == 0) {
    iVar1 = 1 << ((int)*(char *)(local_28[0] + 5) & 0x3fU);
    if (param_1 - 6 < 0x13) {
                    /* WARNING: Could not recover jumptable at 0x10025120. Too many branches */
                    /* WARNING: Treating indirect jump as call */
      (*(code *)(*(uint *)(PTR_PTR_10025124 + (param_1 - 6) * 4) & 0xfffffffe))();
      return;
    }
    if (((param_1 & 0xfffffffb) != 1) && (iVar1 != 0)) {
      if (param_2 != 0) {
        piStack_18 = piStack_14;
      }
      *piStack_18 = iVar1;
    }
  }
  return;
}

