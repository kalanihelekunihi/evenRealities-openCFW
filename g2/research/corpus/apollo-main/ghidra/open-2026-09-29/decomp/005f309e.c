
undefined8 TT_Set_Var_Design(int param_1,uint param_2,int *param_3)

{
  bool bVar1;
  undefined4 uVar2;
  int *piVar3;
  int iVar4;
  int *piVar5;
  uint uVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  int iVar9;
  uint *puVar10;
  uint uVar11;
  int local_28;
  
  local_28 = 0;
  uVar7 = *(undefined4 *)(param_1 + 100);
  uVar8 = 0;
  bVar1 = false;
  uVar11 = param_2;
  if ((*(int *)(param_1 + 700) != 0) || (local_28 = TT_Get_MM_Var(param_1,0), local_28 == 0)) {
    iVar9 = *(int *)(param_1 + 700);
    puVar10 = *(uint **)(iVar9 + 0xc);
    if (*puVar10 < param_2) {
      param_2 = *puVar10;
    }
    if (*(int *)(iVar9 + 4) == 0) {
      uVar11 = 0;
      uVar2 = ft_mem_realloc(uVar7,4,0,*puVar10,0,&local_28);
      *(undefined4 *)(iVar9 + 4) = uVar2;
      if (local_28 != 0) goto LAB_005f3224;
    }
    piVar5 = *(int **)(iVar9 + 4);
    for (uVar6 = 0; uVar6 < param_2; uVar6 = uVar6 + 1) {
      if (*piVar5 != *param_3) {
        *piVar5 = *param_3;
        bVar1 = true;
      }
      param_3 = param_3 + 1;
      piVar5 = piVar5 + 1;
    }
    if ((*(uint *)(param_1 + 4) & DAT_005f3740) == 0) {
      iVar4 = puVar10[3] + param_2 * 0x18;
      for (; uVar6 < *puVar10; uVar6 = uVar6 + 1) {
        if (*piVar5 != *(int *)(iVar4 + 8)) {
          *piVar5 = *(int *)(iVar4 + 8);
          bVar1 = true;
        }
        iVar4 = iVar4 + 0x18;
        piVar5 = piVar5 + 1;
      }
    }
    else {
      piVar3 = (int *)(*(int *)(puVar10[4] + (*(uint *)(param_1 + 4) >> 0x10) * 0xc + -0xc) +
                      param_2 * 4);
      for (; uVar6 < *puVar10; uVar6 = uVar6 + 1) {
        if (*piVar5 != *piVar3) {
          *piVar5 = *piVar3;
          bVar1 = true;
        }
        piVar3 = piVar3 + 1;
        piVar5 = piVar5 + 1;
      }
    }
    if ((*(int *)(iVar9 + 8) != 0) && (!bVar1)) {
      local_28 = -1;
      goto LAB_005f3230;
    }
    uVar11 = 0;
    uVar8 = ft_mem_realloc(uVar7,4,0,*puVar10,0,&local_28);
    if (local_28 == 0) {
      if (*(char *)(*(int *)(param_1 + 700) + 0x18) == '\0') {
        ft_var_load_avar(param_1);
      }
      ft_var_to_normalized(param_1,param_2,*(undefined4 *)(iVar9 + 4),uVar8);
      local_28 = tt_set_mm_blend(param_1,*puVar10,uVar8,0);
      if (local_28 == 0) {
        if (param_2 == 0) {
          *(uint *)(param_1 + 8) = *(uint *)(param_1 + 8) & 0xffff7fff;
        }
        else {
          *(uint *)(param_1 + 8) = *(uint *)(param_1 + 8) | 0x8000;
        }
      }
    }
  }
LAB_005f3224:
  ft_mem_free(uVar7,uVar8);
LAB_005f3230:
  return CONCAT44(uVar11,local_28);
}

