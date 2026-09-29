
void FUN_004b1488(uint param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  
  iVar1 = *DAT_004b178c;
  iVar3 = param_4 + param_2;
  *(int *)(iVar1 + 0x2c) = param_3;
  uVar2 = param_3 + param_1;
  *(uint *)(iVar1 + 0x24) = param_1;
  *(int *)(iVar1 + 0x28) = param_2;
  *(int *)(iVar1 + 0x30) = param_4;
  if ((int)param_1 < 0) {
    param_1 = 0;
  }
  if (param_2 < 0) {
    param_2 = 0;
  }
  FUN_00514846(0x110,param_1 & 0xffff | param_2 << 0x10);
  FUN_00514846(0x114,uVar2 & 0xffff | iVar3 * 0x10000);
  return;
}

