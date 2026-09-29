
undefined8 ft_glyphslot_alloc_bitmap(int param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int local_18;
  undefined4 uStack_14;
  
  uVar1 = *(undefined4 *)(*(int *)(param_1 + 4) + 100);
  local_18 = param_3;
  uStack_14 = param_4;
  if ((int)((uint)*(byte *)(*(int *)(param_1 + 0x9c) + 4) << 0x1f) < 0) {
    ft_mem_free(uVar1,*(undefined4 *)(param_1 + 0x58));
    *(undefined4 *)(param_1 + 0x58) = 0;
  }
  else {
    *(uint *)(*(int *)(param_1 + 0x9c) + 4) = *(uint *)(*(int *)(param_1 + 0x9c) + 4) | 1;
  }
  uVar1 = ft_mem_alloc(uVar1,param_2,&local_18);
  *(undefined4 *)(param_1 + 0x58) = uVar1;
  return CONCAT44(local_18,local_18);
}

