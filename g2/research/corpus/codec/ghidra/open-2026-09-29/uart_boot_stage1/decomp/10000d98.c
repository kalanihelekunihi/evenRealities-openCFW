
void gx8002_uart_stage1_pmu_dispatch(uint param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  int aiStack_28 [2];
  uint *puStack_20;
  int *piStack_18;
  int *piStack_14;
  
  if (param_1 - 7 < 0x12) {
                    /* WARNING: Could not recover jumptable at 0x10000dac. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (*(code *)(*(uint *)(iRam10000db0 + (param_1 - 7) * 4) & 0xfffffffe))();
    return;
  }
  iVar1 = gx8002_uart_stage1_pmu_fill_desc(param_1,aiStack_28);
  if (iVar1 != 0) goto LAB_10000e00;
  uVar2 = (uint)*(char *)(aiStack_28[0] + 6);
  if (uVar2 == 0xffffffff) goto LAB_10000e00;
  if ((param_1 < 10) && ((1 << (param_1 & 0x3f) & 0x243U) != 0)) {
    uVar3 = *puStack_20;
    if ((uVar3 >> (uVar2 + 1 & 0x3f) & 1) == 0) goto LAB_10000e38;
  }
  else {
    uVar3 = *puStack_20;
LAB_10000e38:
    if (((uVar3 >> (uVar2 & 0x3f) & 1) != 0) && (param_2 != 0)) {
      *piStack_14 = 1 << ((int)*(char *)(aiStack_28[0] + 4) & 0x3fU);
      goto LAB_10000e00;
    }
  }
  *piStack_18 = 1 << ((int)*(char *)(aiStack_28[0] + 4) & 0x3fU);
LAB_10000e00:
  iVar1 = gx8002_uart_stage1_pmu_fill_desc(param_1,aiStack_28);
  if (iVar1 == 0) {
    iVar1 = 1 << ((int)*(char *)(aiStack_28[0] + 5) & 0x3fU);
    if (param_1 - 6 < 0x13) {
                    /* WARNING: Could not recover jumptable at 0x10000e22. Too many branches */
                    /* WARNING: Treating indirect jump as call */
      (*(code *)(*(uint *)(PTR_PTR_10000e24 + (param_1 - 6) * 4) & 0xfffffffe))();
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

