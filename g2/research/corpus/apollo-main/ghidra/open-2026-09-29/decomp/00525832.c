
undefined4 destroy_size(undefined4 param_1,int param_2,int param_3)

{
  if (*(int *)(param_2 + 8) != 0) {
    (**(code **)(param_2 + 8))(param_2);
  }
  if (*(int *)(*(int *)(param_3 + 0xc) + 0x3c) != 0) {
    (**(code **)(*(int *)(param_3 + 0xc) + 0x3c))(param_2);
  }
  ft_mem_free(param_1,*(undefined4 *)(param_2 + 0x28));
  *(undefined4 *)(param_2 + 0x28) = 0;
  ft_mem_free(param_1,param_2);
  return 0;
}

