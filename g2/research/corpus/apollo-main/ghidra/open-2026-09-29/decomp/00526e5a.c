
int FT_CMap_New(undefined4 *param_1,undefined4 param_2,int *param_3,undefined4 *param_4)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  int local_28;
  undefined4 *puStack_24;
  
  local_28 = 0;
  if (((param_1 == (undefined4 *)0x0) || (param_3 == (int *)0x0)) || (*param_3 == 0)) {
    return 6;
  }
  iVar4 = *param_3;
  uVar5 = *(undefined4 *)(iVar4 + 100);
  puStack_24 = param_4;
  piVar1 = (int *)ft_mem_alloc(uVar5,*param_1,&local_28,param_4,param_1,param_2);
  if (local_28 == 0) {
    iVar2 = param_3[1];
    iVar3 = param_3[2];
    *piVar1 = *param_3;
    piVar1[1] = iVar2;
    piVar1[2] = iVar3;
    piVar1[3] = (int)param_1;
    if ((param_1[1] == 0) || (local_28 = (*(code *)param_1[1])(piVar1,param_2), local_28 == 0)) {
      uVar5 = ft_mem_realloc(uVar5,4,*(undefined4 *)(iVar4 + 0x24),*(int *)(iVar4 + 0x24) + 1,
                             *(undefined4 *)(iVar4 + 0x28),&local_28);
      *(undefined4 *)(iVar4 + 0x28) = uVar5;
      if (local_28 == 0) {
        iVar2 = *(int *)(iVar4 + 0x24);
        *(int *)(iVar4 + 0x24) = iVar2 + 1;
        *(int **)(*(int *)(iVar4 + 0x28) + iVar2 * 4) = piVar1;
        goto LAB_00526f02;
      }
    }
    ft_cmap_done_internal(piVar1);
    piVar1 = (int *)0x0;
  }
LAB_00526f02:
  if (param_4 != (undefined4 *)0x0) {
    *param_4 = piVar1;
  }
  return local_28;
}

