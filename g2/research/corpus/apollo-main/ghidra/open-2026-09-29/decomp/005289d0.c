
undefined8 FT_Stream_EnterFrame(int *param_1,uint param_2)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int local_18;
  
  local_18 = 0;
  if (param_1[5] == 0) {
    if (((uint)param_1[2] < (uint)param_1[1]) && (param_2 <= (uint)(param_1[1] - param_1[2]))) {
      param_1[8] = *param_1 + param_1[2];
      param_1[9] = param_1[8] + param_2;
      param_1[2] = param_2 + param_1[2];
    }
    else {
      local_18 = 0x55;
    }
  }
  else {
    iVar3 = param_1[7];
    if ((uint)param_1[1] < param_2) {
      local_18 = 0x55;
    }
    else {
      iVar1 = ft_mem_qalloc(iVar3,param_2,&local_18);
      *param_1 = iVar1;
      if (local_18 == 0) {
        uVar2 = (*(code *)param_1[5])(param_1,param_1[2],*param_1,param_2);
        if (uVar2 < param_2) {
          ft_mem_free(iVar3,*param_1);
          *param_1 = 0;
          local_18 = 0x55;
        }
        param_1[8] = *param_1;
        param_1[9] = param_1[8] + param_2;
        param_1[2] = uVar2 + param_1[2];
      }
    }
  }
  return CONCAT44(local_18,local_18);
}

