
int cff_index_get_name(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  int local_28;
  int local_24;
  undefined4 local_20;
  undefined4 local_1c;
  int local_18;
  undefined4 uStack_14;
  
  piVar1 = (int *)(param_1 + 0x24);
  iVar2 = 0;
  if (*piVar1 != 0) {
    uVar3 = *(undefined4 *)(*piVar1 + 0x1c);
    uStack_14 = param_4;
    local_24 = cff_index_access_element(piVar1,param_2,&local_20,&local_28);
    if (local_24 == 0) {
      iVar2 = ft_mem_alloc(uVar3,local_28 + 1,&local_24);
      if (local_24 == 0) {
        if (local_28 != 0) {
          local_18 = local_28;
          local_1c = local_20;
          FUN_00439be4(iVar2,local_20,local_28);
        }
        *(undefined1 *)(iVar2 + local_28) = 0;
      }
      cff_index_forget_element(piVar1,&local_20);
    }
  }
  return iVar2;
}

