
int FUN_005d04e8(undefined4 *param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  bool bVar1;
  undefined4 uVar2;
  int local_18;
  undefined4 uStack_14;
  
  param_1[8] = param_3;
  local_18 = param_3;
  uStack_14 = param_4;
  uVar2 = ft_mem_realloc(param_3,4,0,param_2,0,&local_18);
  param_1[6] = uVar2;
  if (local_18 == 0) {
    uVar2 = ft_mem_realloc(param_3,4,0,param_2,0,&local_18);
    param_1[7] = uVar2;
    if (local_18 == 0) {
      bVar1 = false;
      goto LAB_005d0530;
    }
  }
  bVar1 = true;
LAB_005d0530:
  if (!bVar1) {
    param_1[4] = param_2;
    param_1[3] = DAT_005d0714;
    param_1[5] = 0;
    *param_1 = 0;
    param_1[2] = 0;
    param_1[1] = 0;
    FUN_00439c04(param_1 + 9,DAT_005d0718,0x10);
  }
  if (local_18 != 0) {
    ft_mem_free(param_3,param_1[6]);
    param_1[6] = 0;
  }
  return local_18;
}

