
undefined8
cff_parser_init(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 *param_4,
               undefined4 param_5,undefined2 param_6,undefined2 param_7)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 *local_28;
  
  uVar2 = *param_4;
  local_28 = param_4;
  FUN_0043c0e4(param_1,0x28,0,param_4,param_1,param_3);
  param_1[7] = param_2;
  param_1[8] = param_3;
  *param_1 = param_4;
  *(undefined2 *)(param_1 + 9) = param_6;
  *(undefined2 *)((int)param_1 + 0x26) = param_7;
  uVar3 = 0;
  uVar1 = ft_mem_realloc(uVar2,4,0,param_5,0,&local_28);
  param_1[4] = uVar1;
  if (local_28 == (undefined4 *)0x0) {
    param_1[6] = param_5;
    param_1[5] = param_1[4];
  }
  else {
    ft_mem_free(uVar2,param_1[4]);
    param_1[4] = 0;
  }
  return CONCAT44(uVar3,local_28);
}

