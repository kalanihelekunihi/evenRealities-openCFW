
undefined4
ft_cmap_done_internal(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  uVar1 = *(undefined4 *)(*param_1 + 100);
  if (*(int *)(param_1[3] + 8) != 0) {
    (**(code **)(param_1[3] + 8))(param_1);
  }
  ft_mem_free(uVar1,param_1);
  return param_4;
}

