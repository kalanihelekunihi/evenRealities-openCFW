
void FUN_004b1ad4(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint in_fpscr;
  undefined4 uVar1;
  undefined4 uVar2;
  
  uVar2 = VectorSignedToFloat(param_2,(byte)(in_fpscr >> 0x16) & 3);
  uVar1 = VectorSignedToFloat(param_1,(byte)(in_fpscr >> 0x16) & 3);
  FUN_005228b0(uVar1,uVar2);
  FUN_00522ae0(param_1,param_2,param_3,param_4);
  return;
}

