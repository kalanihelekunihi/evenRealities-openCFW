
undefined8 FT_New_Size(int param_1,undefined4 *param_2,undefined4 param_3,int param_4)

{
  bool bVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  int local_20;
  
  iVar6 = 0;
  local_20 = param_4;
  if (param_1 == 0) {
    iVar4 = 0x23;
  }
  else if (param_2 == (undefined4 *)0x0) {
    iVar4 = 6;
  }
  else if (*(int *)(param_1 + 0x60) == 0) {
    iVar4 = 0x22;
  }
  else {
    *param_2 = 0;
    iVar4 = *(int *)(*(int *)(param_1 + 0x60) + 0xc);
    uVar5 = *(undefined4 *)(param_1 + 100);
    piVar2 = (int *)ft_mem_alloc(uVar5,*(undefined4 *)(iVar4 + 0x28),&local_20);
    if ((local_20 == 0) && (iVar6 = ft_mem_alloc(uVar5,0xc,&local_20), local_20 == 0)) {
      bVar1 = false;
    }
    else {
      bVar1 = true;
    }
    if (!bVar1) {
      *piVar2 = param_1;
      iVar3 = ft_mem_alloc(uVar5,0x24,&local_20);
      if (local_20 == 0) {
        piVar2[10] = iVar3;
        if (*(int *)(iVar4 + 0x38) != 0) {
          local_20 = (**(code **)(iVar4 + 0x38))(piVar2);
        }
        if (local_20 == 0) {
          *param_2 = piVar2;
          *(int **)(iVar6 + 8) = piVar2;
          FT_List_Add(param_1 + 0x6c,iVar6);
        }
      }
    }
    iVar4 = local_20;
    if (local_20 != 0) {
      ft_mem_free(uVar5,iVar6);
      ft_mem_free(uVar5,piVar2);
      iVar4 = local_20;
    }
  }
  return CONCAT44(local_20,iVar4);
}

