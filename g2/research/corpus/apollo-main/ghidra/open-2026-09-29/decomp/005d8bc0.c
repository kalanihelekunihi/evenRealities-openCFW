
undefined8 FUN_005d8bc0(int param_1,int param_2,undefined4 param_3)

{
  undefined4 uVar1;
  uint uVar2;
  uint uVar3;
  int local_10;
  
  uVar2 = *(int *)(param_1 + 4) + 7U >> 3;
  uVar3 = param_2 + 7U >> 3;
  local_10 = 0;
  if (uVar2 < uVar3) {
    uVar3 = uVar3 + 7 & 0xfffffff8;
    param_2 = *(int *)(param_1 + 8);
    uVar1 = ft_mem_realloc(param_3,1,uVar2,uVar3,param_2,&local_10);
    *(undefined4 *)(param_1 + 8) = uVar1;
    if (local_10 == 0) {
      *(uint *)(param_1 + 4) = uVar3 << 3;
    }
  }
  return CONCAT44(param_2,local_10);
}

