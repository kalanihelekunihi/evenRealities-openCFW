
undefined8 FT_Add_Module(int *param_1,int param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  uint uVar4;
  int local_18;
  
  local_18 = param_4;
  if (param_1 == (int *)0x0) {
    iVar1 = 0x21;
  }
  else if (param_2 == 0) {
    iVar1 = 6;
  }
  else if (*(int *)(param_2 + 0x10) < DAT_00527b5c) {
    for (uVar4 = 0; uVar4 < (uint)param_1[4]; uVar4 = uVar4 + 1) {
      piVar2 = (int *)param_1[uVar4 + 5];
      iVar1 = FUN_0046cacc(*(undefined4 *)(*piVar2 + 8),*(undefined4 *)(param_2 + 8));
      if (iVar1 == 0) {
        if (*(int *)(param_2 + 0xc) <= *(int *)(*piVar2 + 0xc)) {
          iVar1 = 5;
          goto LAB_005272aa;
        }
        FT_Remove_Module(param_1,piVar2);
        break;
      }
    }
    iVar3 = *param_1;
    local_18 = 0;
    if ((uint)param_1[4] < 0x20) {
      piVar2 = (int *)ft_mem_alloc(iVar3,*(undefined4 *)(param_2 + 4),&local_18);
      iVar1 = local_18;
      if (local_18 == 0) {
        piVar2[1] = (int)param_1;
        piVar2[2] = iVar3;
        *piVar2 = param_2;
        if ((-1 < (int)((uint)*(byte *)*piVar2 << 0x1e)) ||
           (local_18 = ft_add_renderer(piVar2), local_18 == 0)) {
          if ((int)((uint)*(byte *)*piVar2 << 0x1d) < 0) {
            param_1[0x28] = (int)piVar2;
          }
          if ((int)((uint)*(byte *)*piVar2 << 0x1f) < 0) {
            piVar2[3] = *piVar2;
          }
          if ((*(int *)(param_2 + 0x18) == 0) ||
             (local_18 = (**(code **)(param_2 + 0x18))(piVar2), local_18 == 0)) {
            iVar1 = param_1[4];
            param_1[4] = iVar1 + 1;
            param_1[iVar1 + 5] = (int)piVar2;
            iVar1 = local_18;
            goto LAB_005272aa;
          }
        }
        if (((int)((uint)*(byte *)*piVar2 << 0x1e) < 0) &&
           (((piVar2[3] != 0 && (*(int *)(piVar2[3] + 0x24) == DAT_00527500)) && (piVar2[0xd] != 0))
           )) {
          (**(code **)(*(int *)(piVar2[3] + 0x38) + 0x14))(piVar2[0xd]);
        }
        ft_mem_free(iVar3,piVar2);
        iVar1 = local_18;
      }
    }
    else {
      local_18 = 0x30;
      iVar1 = local_18;
    }
  }
  else {
    iVar1 = 4;
  }
LAB_005272aa:
  return CONCAT44(local_18,iVar1);
}

