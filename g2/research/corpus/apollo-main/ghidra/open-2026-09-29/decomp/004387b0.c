
/* WARNING: Control flow encountered bad instruction data */

void FUN_004387b0(int param_1,int param_2,int param_3,undefined4 *param_4,int param_5)

{
  uint in_fpscr;
  undefined4 uVar1;
  undefined4 uVar2;
  
  for (; 3 < param_5; param_5 = param_5 + -4) {
    if (0 < param_3 >> 3) {
      VectorLoadRegister(param_1 + -0x200,1,2,0);
      VectorLoadRegister(param_2 + -0x202,1,2,0);
      VectorLoadRegister(param_2 + -0x200,1,2,0);
      VectorLoadRegister(param_2 + -0x204,1,2,0);
                    /* WARNING: Bad instruction - Truncating control flow here */
      halt_baddata();
    }
    uVar1 = VectorSignedToFloat(0,(byte)(in_fpscr >> 0x16) & 3);
    *param_4 = uVar1;
    uVar1 = VectorSignedToFloat(0,(byte)(in_fpscr >> 0x16) & 3);
    param_4[1] = uVar1;
    uVar1 = VectorSignedToFloat(0,(byte)(in_fpscr >> 0x16) & 3);
    uVar2 = VectorSignedToFloat(0,(byte)(in_fpscr >> 0x16) & 3);
    param_4[2] = uVar1;
    param_4[3] = uVar2;
    param_4 = param_4 + 4;
    param_2 = param_2 + -8;
  }
  while( true ) {
    if (param_5 < 1) {
      return;
    }
    if (0 < param_3 >> 3) break;
    param_2 = param_2 + -2;
    param_5 = param_5 + -1;
    uVar1 = VectorSignedToFloat(0,(byte)(in_fpscr >> 0x16) & 3);
    *param_4 = uVar1;
    param_4 = param_4 + 1;
  }
  VectorLoadRegister(param_1 + -0x200,1,2,0);
  VectorLoadRegister(param_2 + -0x200,1,2,0);
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}

