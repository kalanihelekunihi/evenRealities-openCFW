
undefined8 af_axis_hints_new_segment(int *param_1,int param_2,int *param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int local_18;
  
  local_18 = 0;
  iVar3 = 0;
  iVar4 = param_2;
  if (*param_1 < 0x12) {
    if (param_1[2] == 0) {
      param_1[2] = (int)(param_1 + 7);
      param_1[1] = 0x12;
    }
  }
  else if (param_1[1] <= *param_1) {
    iVar1 = param_1[1];
    if (DAT_005a8a44 <= iVar1) {
      local_18 = 0x40;
      goto LAB_005a7e64;
    }
    iVar2 = iVar1 + (iVar1 >> 2) + 4;
    if ((iVar2 < iVar1) || (DAT_005a8a44 < iVar2)) {
      iVar2 = DAT_005a8a44;
    }
    if ((int *)param_1[2] == param_1 + 7) {
      iVar4 = 0;
      iVar1 = ft_mem_realloc(param_2,0x2c,0,iVar2,0,&local_18);
      param_1[2] = iVar1;
      if (local_18 != 0) goto LAB_005a7e64;
      FUN_00439be4(param_1[2],param_1 + 7,0x318);
    }
    else {
      iVar4 = param_1[2];
      iVar1 = ft_mem_realloc(param_2,0x2c,iVar1,iVar2,iVar4,&local_18);
      param_1[2] = iVar1;
      if (local_18 != 0) goto LAB_005a7e64;
    }
    param_1[1] = iVar2;
  }
  iVar3 = *param_1;
  *param_1 = iVar3 + 1;
  iVar3 = param_1[2] + iVar3 * 0x2c;
LAB_005a7e64:
  *param_3 = iVar3;
  return CONCAT44(iVar4,local_18);
}

