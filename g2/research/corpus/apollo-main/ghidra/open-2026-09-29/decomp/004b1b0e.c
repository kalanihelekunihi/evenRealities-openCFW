
void FUN_004b1b0e(int param_1,int param_2,undefined4 param_3,undefined4 param_4,int param_5,
                 int param_6)

{
  uint in_fpscr;
  undefined4 uVar1;
  undefined4 uVar2;
  
  uVar2 = VectorSignedToFloat(param_2 - param_6,(byte)(in_fpscr >> 0x16) & 3);
  uVar1 = VectorSignedToFloat(param_1 - param_5,(byte)(in_fpscr >> 0x16) & 3);
  FUN_005228b0(uVar1,uVar2);
  FUN_00522ae0(param_1,param_2,param_3,param_4);
  return;
}

