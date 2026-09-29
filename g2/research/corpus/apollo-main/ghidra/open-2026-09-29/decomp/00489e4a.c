
undefined8 FUN_00489e4a(undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint local_18;
  undefined4 uStack_14;
  
  local_18 = 0;
  iVar1 = 0;
  uStack_14 = param_4;
  while (local_18 < param_2) {
    (*(code *)*DAT_00489eac)(param_1,&local_18);
    iVar1 = iVar1 + 1;
  }
  return CONCAT44(local_18,iVar1);
}

