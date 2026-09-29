
/* WARNING: Control flow encountered bad instruction data */

void FUN_1000f0c0(undefined4 param_1,int param_2,undefined4 param_3,uint param_4)

{
  if (param_2 < 0) {
    dsp_stub();
    if (param_4 >> 2 != 0) {
      dsp_stub();
                    /* WARNING: Bad instruction - Truncating control flow here */
      halt_baddata();
    }
    if ((param_4 & 3) != 0) {
      dsp_stub();
                    /* WARNING: Bad instruction - Truncating control flow here */
      halt_baddata();
    }
  }
  else {
    if (param_4 >> 2 != 0) {
      dsp_stub();
                    /* WARNING: Bad instruction - Truncating control flow here */
      halt_baddata();
    }
    if ((param_4 & 3) != 0) {
      dsp_stub();
                    /* WARNING: Bad instruction - Truncating control flow here */
      halt_baddata();
    }
  }
  return;
}

