
void FUN_005d4c88(undefined4 param_1,int *param_2,int *param_3,undefined4 param_4,int param_5,
                 char param_6)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  bool bVar5;
  int local_60 [15];
  
  local_60[0xe] = param_4;
  local_60[0] = *param_2;
  local_60[1] = *param_3;
  iVar2 = 0;
  bVar5 = *(char *)(param_5 + 9) == '\0';
  if (bVar5) {
    iVar3 = 9;
  }
  else {
    iVar3 = 10;
  }
  for (iVar4 = 0; iVar4 < iVar3; iVar4 = iVar4 + 1) {
    local_60[iVar4 + 2] = local_60[iVar4];
    if (*(char *)(param_5 + iVar4) != '\0') {
      iVar1 = FUN_005d6f38(param_1,iVar2);
      iVar2 = iVar2 + 1;
      local_60[iVar4 + 2] = iVar1 + local_60[iVar4 + 2];
    }
  }
  if (bVar5) {
    local_60[0xb] = *param_3;
  }
  if (param_6 == '\0') {
    if (*(char *)(param_5 + 10) == '\0') {
      local_60[0xc] = *param_2;
    }
    else {
      iVar3 = FUN_005d6f38(param_1,iVar2);
      iVar2 = iVar2 + 1;
      local_60[0xc] = iVar3 + local_60[10];
    }
    iVar3 = local_60[0xb];
    if (*(char *)(param_5 + 0xb) == '\0') {
      local_60[0xd] = *param_3;
    }
    else {
      iVar2 = FUN_005d6f38(param_1,iVar2);
      local_60[0xd] = iVar2 + iVar3;
    }
  }
  else {
    if (local_60[0xb] - *param_3 < 0) {
      iVar3 = *param_3 - local_60[0xb];
    }
    else {
      iVar3 = local_60[0xb] - *param_3;
    }
    if (local_60[10] - *param_2 < 0) {
      iVar4 = *param_2 - local_60[10];
    }
    else {
      iVar4 = local_60[10] - *param_2;
    }
    iVar2 = FUN_005d6f38(param_1,iVar2);
    if (iVar3 < iVar4) {
      local_60[0xc] = iVar2 + local_60[10];
      local_60[0xd] = *param_3;
    }
    else {
      local_60[0xc] = *param_2;
      local_60[0xd] = iVar2 + local_60[0xb];
    }
  }
  for (iVar2 = 0; iVar2 < 2; iVar2 = iVar2 + 1) {
    FUN_005d4912(param_4,local_60[iVar2 * 6 + 2],local_60[iVar2 * 6 + 3],local_60[iVar2 * 6 + 4],
                 local_60[iVar2 * 6 + 5],local_60[iVar2 * 6 + 6],local_60[iVar2 * 6 + 7]);
  }
  FUN_005d709c(param_1);
  *param_2 = local_60[0xc];
  *param_3 = local_60[0xd];
  return;
}

