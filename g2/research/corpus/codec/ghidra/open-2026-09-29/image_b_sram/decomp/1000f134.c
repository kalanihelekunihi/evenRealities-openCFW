
/* WARNING: Control flow encountered bad instruction data */

void FUN_1000f134(undefined4 param_1,undefined2 *param_2,uint param_3)

{
  if (param_3 >> 2 != 0) {
    dsp_stub();
    dsp_stub();
    dsp_stub();
    dsp_stub();
    dsp_stub();
                    /* WARNING: Bad instruction - Truncating control flow here */
    halt_baddata();
  }
  if ((param_3 & 3) != 0) {
    dsp_stub();
    dsp_stub();
                    /* WARNING: Bad instruction - Truncating control flow here */
    halt_baddata();
  }
  dsp_stub();
  dsp_stub();
  dsp_stub();
  *param_2 = 0;
  return;
}

