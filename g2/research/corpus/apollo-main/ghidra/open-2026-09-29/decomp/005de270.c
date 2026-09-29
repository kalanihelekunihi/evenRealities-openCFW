
undefined8 FUN_005de270(int param_1,uint param_2,undefined4 param_3)

{
  undefined4 uVar1;
  uint uVar2;
  int local_10;
  
  local_10 = 0;
  uVar2 = param_2;
  if (*(uint *)(param_1 + 0x1c) < param_2) {
    *(undefined4 *)(param_1 + 0x24) = param_3;
    uVar2 = *(uint *)(param_1 + 0x20);
    uVar1 = ft_mem_realloc(param_3,4,*(undefined4 *)(param_1 + 0x1c),param_2,uVar2,&local_10);
    *(undefined4 *)(param_1 + 0x20) = uVar1;
    if (local_10 == 0) {
      *(uint *)(param_1 + 0x1c) = param_2;
    }
  }
  return CONCAT44(uVar2,local_10);
}

