
undefined4 Destroy_Module(int *param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = param_1[2];
  iVar3 = *param_1;
  iVar1 = param_1[1];
  if ((iVar1 != 0) && (*(int **)(iVar1 + 0xa0) == param_1)) {
    *(undefined4 *)(iVar1 + 0xa0) = 0;
  }
  if ((int)((uint)*(byte *)*param_1 << 0x1e) < 0) {
    ft_remove_renderer(param_1);
  }
  if ((int)((uint)*(byte *)*param_1 << 0x1f) < 0) {
    Destroy_Driver(param_1);
  }
  if (*(int *)(iVar3 + 0x1c) != 0) {
    (**(code **)(iVar3 + 0x1c))(param_1);
  }
  ft_mem_free(iVar2,param_1);
  return 0;
}

