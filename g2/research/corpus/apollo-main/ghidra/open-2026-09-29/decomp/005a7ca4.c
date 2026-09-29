
undefined4 af_face_globals_free(int *param_1)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  if (param_1 != (int *)0x0) {
    uVar2 = *(undefined4 *)(*param_1 + 100);
    for (uVar3 = 0; uVar3 < 0x54; uVar3 = uVar3 + 1) {
      if (param_1[uVar3 + 4] != 0) {
        iVar1 = *(int *)(DAT_005a7fb0 + (uint)*(byte *)(*(int *)(DAT_005a7fa8 + uVar3 * 4) + 1) * 4)
        ;
        if (*(int *)(iVar1 + 0x10) != 0) {
          (**(code **)(iVar1 + 0x10))(param_1[uVar3 + 4]);
        }
        ft_mem_free(uVar2,param_1[uVar3 + 4]);
        param_1[uVar3 + 4] = 0;
      }
    }
    ft_mem_free(uVar2,param_1);
  }
  return 0;
}

