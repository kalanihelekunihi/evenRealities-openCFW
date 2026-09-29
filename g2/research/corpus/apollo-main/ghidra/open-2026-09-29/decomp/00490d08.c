
void FUN_00490d08(undefined4 param_1,undefined4 param_2,uint param_3,int param_4)

{
  uint uVar1;
  uint uVar2;
  
  if (param_4 < 0) {
    uVar1 = ~(param_3 << 1);
    uVar2 = ~(param_4 << 1 | param_3 >> 0x1f);
  }
  else {
    uVar2 = param_4 << 1 | param_3 >> 0x1f;
    uVar1 = param_3 << 1;
  }
  FUN_00490ce0(param_1,param_2,uVar1,uVar2,param_4);
  return;
}

