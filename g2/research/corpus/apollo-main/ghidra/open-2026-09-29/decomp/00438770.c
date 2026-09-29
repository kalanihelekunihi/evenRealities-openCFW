
/* WARNING: Control flow encountered bad instruction data */

undefined4 FUN_00438770(int param_1,int param_2,int param_3)

{
  uint in_fpscr;
  undefined4 uVar1;
  
  if (0 < param_3 >> 3) {
    VectorLoadRegister(param_1 + -0x200,1,2,0);
    VectorLoadRegister(param_2 + -0x200,1,2,0);
                    /* WARNING: Bad instruction - Truncating control flow here */
    halt_baddata();
  }
  uVar1 = VectorSignedToFloat(0,(byte)(in_fpscr >> 0x16) & 3);
  return uVar1;
}

