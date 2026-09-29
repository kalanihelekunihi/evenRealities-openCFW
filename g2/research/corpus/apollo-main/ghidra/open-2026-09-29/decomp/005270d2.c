
undefined8 ft_add_renderer(int *param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 *puVar3;
  int iVar4;
  int local_20;
  
  puVar3 = (undefined4 *)param_1[1];
  uVar2 = *puVar3;
  local_20 = param_4;
  iVar1 = ft_mem_alloc(uVar2,0xc,&local_20);
  if (local_20 != 0) goto LAB_00527166;
  iVar4 = *param_1;
  param_1[3] = iVar4;
  param_1[4] = *(int *)(iVar4 + 0x24);
  if ((*(int *)(iVar4 + 0x24) == DAT_00527500) && (*(int *)(*(int *)(iVar4 + 0x38) + 4) != 0)) {
    local_20 = (**(code **)(*(int *)(iVar4 + 0x38) + 4))(uVar2,param_1 + 0xd);
    if (local_20 == 0) {
      param_1[0xe] = *(int *)(*(int *)(iVar4 + 0x38) + 0x10);
      param_1[0xf] = *(int *)(iVar4 + 0x28);
      goto LAB_00527144;
    }
  }
  else {
LAB_00527144:
    *(int **)(iVar1 + 8) = param_1;
    FT_List_Add(puVar3 + 0x25,iVar1);
    ft_set_current_renderer(puVar3);
  }
  if (local_20 != 0) {
    ft_mem_free(uVar2,iVar1);
  }
LAB_00527166:
  return CONCAT44(local_20,local_20);
}

