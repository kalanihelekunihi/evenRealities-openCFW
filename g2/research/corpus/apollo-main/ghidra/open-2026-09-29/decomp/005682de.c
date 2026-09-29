
undefined8 FUN_005682de(int *param_1,int param_2)

{
  bool bVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  int local_18;
  
  uVar3 = param_1[1];
  local_18 = 0;
  if ((uint)(param_2 + *param_1) <= uVar3) goto LAB_00568346;
  iVar5 = param_1[6];
  for (uVar4 = uVar3; uVar4 < (uint)(param_2 + *param_1); uVar4 = uVar4 + (uVar4 >> 1) + 0x10) {
  }
  param_2 = param_1[2];
  iVar2 = ft_mem_realloc(iVar5,8,uVar3,uVar4,param_2,&local_18);
  param_1[2] = iVar2;
  if (local_18 == 0) {
    param_2 = param_1[3];
    iVar5 = ft_mem_realloc(iVar5,1,uVar3,uVar4,param_2,&local_18);
    param_1[3] = iVar5;
    if (local_18 != 0) goto LAB_00568338;
    bVar1 = false;
  }
  else {
LAB_00568338:
    bVar1 = true;
  }
  if (!bVar1) {
    param_1[1] = uVar4;
  }
LAB_00568346:
  return CONCAT44(param_2,local_18);
}

