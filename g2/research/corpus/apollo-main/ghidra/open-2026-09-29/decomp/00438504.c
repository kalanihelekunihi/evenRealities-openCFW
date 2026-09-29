
/* WARNING: Control flow encountered bad instruction data */

void FUN_00438504(undefined4 param_1,int param_2,undefined4 param_3,int param_4)

{
  if (0 < param_4 * 5) {
    VectorLoadRegister(param_2 + -0x24e,1,2,0);
    VectorLoadRegister(DAT_00438fb0 + -0x200,1,2,0);
                    /* WARNING: Bad instruction - Truncating control flow here */
    halt_baddata();
  }
  return;
}

