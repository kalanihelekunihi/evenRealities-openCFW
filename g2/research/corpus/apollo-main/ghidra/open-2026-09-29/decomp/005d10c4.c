
int FUN_005d10c4(undefined4 *param_1,int param_2,int *param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 *puVar4;
  uint local_1c4;
  undefined1 auStack_1c0 [5];
  undefined1 local_1bb;
  int local_1b4;
  byte local_1b0;
  undefined4 local_1a0 [96];
  
  iVar1 = 0;
  FUN_00439c04(auStack_1c0,param_2,0x20);
  local_1bb = 2;
  if ((*(char *)(param_2 + 5) == '\n') || (*(char *)(param_2 + 5) == '\a')) {
    local_1bb = 3;
  }
  FUN_005d0b7c(param_1,local_1a0,0x20,&local_1c4);
  if ((int)local_1c4 < 0) {
    iVar1 = 0xa2;
  }
  else {
    if (*(uint *)(param_2 + 0x14) < local_1c4) {
      local_1c4 = *(uint *)(param_2 + 0x14);
    }
    uVar2 = *param_1;
    uVar3 = param_1[2];
    if ((*(char *)(param_2 + 5) != '\a') && (*(int *)(param_2 + 0x18) != 0)) {
      *(char *)(*param_3 + *(int *)(param_2 + 0x18)) = (char)local_1c4;
    }
    puVar4 = local_1a0;
    for (; 0 < (int)local_1c4; local_1c4 = local_1c4 - 1) {
      *param_1 = *puVar4;
      param_1[2] = puVar4[1];
      iVar1 = FUN_005d0de0(param_1,auStack_1c0,param_3,param_4,0);
      if (iVar1 != 0) break;
      local_1b4 = local_1b4 + (uint)local_1b0;
      puVar4 = puVar4 + 3;
    }
    *param_1 = uVar2;
    param_1[2] = uVar3;
  }
  return iVar1;
}

