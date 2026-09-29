
void FUN_005f9f14(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint in_fpscr;
  
  VectorSignedToFloat(param_4,(byte)(in_fpscr >> 0x16) & 3);
  VectorSignedToFloat(param_3,(byte)(in_fpscr >> 0x16) & 3);
  FUN_004b199c();
  return;
}

