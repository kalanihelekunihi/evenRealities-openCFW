
void FUN_004b1516(uint param_1,int param_2,int param_3,int param_4)

{
  uint uVar1;
  
  uVar1 = param_3 + param_1;
  param_4 = param_4 + param_2;
  if ((int)param_1 < 0) {
    param_1 = 0;
  }
  if (param_2 < 0) {
    param_2 = 0;
  }
  FUN_00514846(0x110,param_1 & 0xffff | param_2 << 0x10);
  FUN_00514846(0x114,uVar1 & 0xffff | param_4 * 0x10000);
  return;
}

