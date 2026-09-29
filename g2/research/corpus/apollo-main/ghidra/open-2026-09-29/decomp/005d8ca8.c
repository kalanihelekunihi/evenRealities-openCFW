
undefined8 FUN_005d8ca8(int param_1,uint param_2,undefined4 param_3)

{
  undefined4 uVar1;
  uint uVar2;
  int local_10;
  
  local_10 = 0;
  if (*(uint *)(param_1 + 4) < param_2) {
    uVar2 = param_2 + 7 & 0xfffffff8;
    param_2 = *(uint *)(param_1 + 8);
    uVar1 = ft_mem_realloc(param_3,0x10,*(uint *)(param_1 + 4),uVar2,param_2,&local_10);
    *(undefined4 *)(param_1 + 8) = uVar1;
    if (local_10 == 0) {
      *(uint *)(param_1 + 4) = uVar2;
    }
  }
  return CONCAT44(param_2,local_10);
}

