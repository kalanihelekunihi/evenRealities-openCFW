
void FUN_004b14ca(uint param_1,int param_2,int param_3,int param_4)

{
  uint uVar1;
  
  if ((int)param_1 < 1) {
    uVar1 = 0;
  }
  else {
    uVar1 = param_1 & 0xffff;
  }
  if (0 < param_2) {
    uVar1 = uVar1 | param_2 << 0x10;
  }
  FUN_00514846(0x158,uVar1);
  FUN_00514846(0x15c,param_3 + param_1 & 0xffff | (param_4 + param_2) * 0x10000);
  return;
}

