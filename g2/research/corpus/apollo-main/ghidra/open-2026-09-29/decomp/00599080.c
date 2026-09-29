
void FUN_00599080(int param_1,undefined4 param_2,int param_3)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = FUN_00599050(param_2);
  if (iVar1 < 1) {
    return;
  }
  uVar2 = *(uint *)(param_1 + 0x20);
  iVar1 = iVar1 + uVar2;
  if (iVar1 < 0x21) {
    *(int *)(param_1 + 0x20) = iVar1;
    *(uint *)(param_1 + 0x1c) = param_3 << (uVar2 & 0xff) | *(uint *)(param_1 + 0x1c);
    return;
  }
  FUN_00439b12(param_1,param_3);
  return;
}

