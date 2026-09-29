
void FUN_004991e0(int param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int local_34;
  int local_30;
  int local_2c;
  int local_28;
  undefined1 auStack_24 [8];
  
  FUN_0043f66c(param_1);
  uVar1 = FUN_0043fd9e(param_1);
  uVar2 = FUN_0043fdda(param_1);
  FUN_00498b82(param_1,auStack_24);
  FUN_00488cda(&local_34,uVar1,uVar2,*(undefined4 *)(param_1 + 0x44),
               *(uint *)(param_1 + 0x48) & 0xffff,*(uint *)(param_1 + 0x4c) & 0xffff,auStack_24);
  local_34 = *(int *)(param_1 + 0x14) + local_34 + -1;
  local_30 = *(int *)(param_1 + 0x18) + local_30 + -1;
  local_2c = *(int *)(param_1 + 0x14) + local_2c + 1;
  local_28 = *(int *)(param_1 + 0x18) + local_28 + 1;
  FUN_004405d4(param_1,&local_34);
  *(undefined4 *)(param_1 + 0x48) = param_2;
  *(undefined4 *)(param_1 + 0x4c) = param_3;
  uVar3 = FUN_0044dc0a(param_1);
  FUN_0044fe8e(uVar3,0);
  FUN_00452d42(param_1);
  FUN_0044fe8e(uVar3,1);
  FUN_00488cda(&local_34,uVar1,uVar2,*(undefined4 *)(param_1 + 0x44),
               *(uint *)(param_1 + 0x48) & 0xffff,*(uint *)(param_1 + 0x4c) & 0xffff,auStack_24);
  local_34 = *(int *)(param_1 + 0x14) + local_34 + -1;
  local_30 = *(int *)(param_1 + 0x18) + local_30 + -1;
  local_2c = *(int *)(param_1 + 0x14) + local_2c + 1;
  local_28 = *(int *)(param_1 + 0x18) + local_28 + 1;
  FUN_004405d4(param_1,&local_34);
  return;
}

