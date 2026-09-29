
undefined4 cff_size_done(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined4 uVar4;
  
  uVar4 = *(undefined4 *)(*param_1 + 100);
  iVar2 = *(int *)(*param_1 + 0x2a4);
  puVar3 = *(undefined4 **)param_1[10];
  if (puVar3 != (undefined4 *)0x0) {
    iVar1 = cff_size_get_globals_funcs(param_1);
    if (iVar1 != 0) {
      (**(code **)(iVar1 + 8))(*puVar3);
      for (iVar2 = *(int *)(iVar2 + 0x7e8); iVar2 != 0; iVar2 = iVar2 + -1) {
        (**(code **)(iVar1 + 8))(puVar3[iVar2]);
      }
    }
    ft_mem_free(uVar4,puVar3);
  }
  return param_4;
}

