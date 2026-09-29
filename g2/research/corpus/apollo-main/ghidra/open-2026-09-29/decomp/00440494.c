
void FUN_00440494(undefined4 param_1,int *param_2,undefined1 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int local_30;
  int local_2c;
  int local_28;
  int local_24;
  int local_20;
  int local_1c;
  int local_18;
  int local_14;
  undefined4 uStack_10;
  
  local_30 = *param_2;
  local_2c = param_2[1];
  local_28 = *param_2;
  local_24 = param_2[3] + 1;
  local_20 = param_2[2] + 1;
  local_1c = param_2[1];
  local_18 = param_2[2] + 1;
  local_14 = param_2[3] + 1;
  uStack_10 = param_4;
  FUN_004403e6(param_1,&local_30,4,param_3);
  iVar1 = local_28;
  if (local_30 < local_28) {
    iVar1 = local_30;
  }
  iVar2 = local_18;
  if (local_20 < local_18) {
    iVar2 = local_20;
  }
  if (iVar1 < iVar2) {
    iVar1 = local_28;
    if (local_30 < local_28) {
      iVar1 = local_30;
    }
  }
  else {
    iVar1 = local_18;
    if (local_20 < local_18) {
      iVar1 = local_20;
    }
  }
  *param_2 = iVar1;
  iVar1 = local_18;
  if (local_18 < local_20) {
    iVar1 = local_20;
  }
  iVar2 = local_28;
  if (local_28 < local_30) {
    iVar2 = local_30;
  }
  if (iVar1 < iVar2) {
    local_18 = local_28;
    if (local_28 < local_30) {
      local_18 = local_30;
    }
  }
  else if (local_18 < local_20) {
    local_18 = local_20;
  }
  param_2[2] = local_18;
  iVar1 = local_24;
  if (local_2c < local_24) {
    iVar1 = local_2c;
  }
  iVar2 = local_14;
  if (local_1c < local_14) {
    iVar2 = local_1c;
  }
  if (iVar1 < iVar2) {
    iVar1 = local_24;
    if (local_2c < local_24) {
      iVar1 = local_2c;
    }
  }
  else {
    iVar1 = local_14;
    if (local_1c < local_14) {
      iVar1 = local_1c;
    }
  }
  param_2[1] = iVar1;
  iVar1 = local_14;
  if (local_14 < local_1c) {
    iVar1 = local_1c;
  }
  iVar2 = local_24;
  if (local_24 < local_2c) {
    iVar2 = local_2c;
  }
  if (iVar1 < iVar2) {
    local_14 = local_24;
    if (local_24 < local_2c) {
      local_14 = local_2c;
    }
  }
  else if (local_14 < local_1c) {
    local_14 = local_1c;
  }
  param_2[3] = local_14;
  return;
}

