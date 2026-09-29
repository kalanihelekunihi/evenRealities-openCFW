
undefined8 FUN_005cd728(int param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  int local_18;
  int local_14;
  int local_10;
  int local_c;
  
  local_18 = param_1;
  local_14 = param_2;
  local_10 = param_3;
  local_c = param_4;
  FUN_005cd638(param_1,*(undefined4 *)(param_1 + 0x44),*(undefined4 *)(param_1 + 0x40),&local_18);
  if (local_18 < 0) {
    FUN_0044e79e(param_1,-local_18,0,1);
  }
  else {
    iVar1 = FUN_0043fd9e(param_1);
    if (iVar1 < local_10) {
      iVar1 = FUN_0043fd9e(param_1);
      FUN_0044e79e(param_1,iVar1 - local_10,0,1);
    }
  }
  if (local_14 < 0) {
    FUN_0044e79e(param_1,0,-local_14,1);
  }
  else {
    iVar1 = FUN_0043fdda(param_1);
    if (iVar1 < local_c) {
      iVar1 = FUN_0043fdda(param_1);
      FUN_0044e79e(param_1,0,iVar1 - local_c,1);
    }
  }
  return CONCAT44(local_14,local_18);
}

