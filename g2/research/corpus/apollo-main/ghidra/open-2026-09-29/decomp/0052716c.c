
undefined4 ft_remove_renderer(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  
  puVar2 = *(undefined4 **)(param_1 + 4);
  if (puVar2 != (undefined4 *)0x0) {
    uVar3 = *puVar2;
    iVar1 = FT_List_Find(puVar2 + 0x25,param_1);
    if (iVar1 != 0) {
      if ((*(int *)(*(int *)(param_1 + 0xc) + 0x24) == DAT_00527500) &&
         (*(int *)(param_1 + 0x34) != 0)) {
        (**(code **)(*(int *)(*(int *)(param_1 + 0xc) + 0x38) + 0x14))
                  (*(undefined4 *)(param_1 + 0x34));
      }
      FT_List_Remove(puVar2 + 0x25,iVar1);
      ft_mem_free(uVar3,iVar1);
      ft_set_current_renderer(puVar2);
    }
  }
  return param_4;
}

