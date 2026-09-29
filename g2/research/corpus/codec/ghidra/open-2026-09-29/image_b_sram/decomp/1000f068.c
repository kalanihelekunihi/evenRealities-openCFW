
/* WARNING: Control flow encountered bad instruction data */

void FUN_1000f068(undefined4 param_1,int param_2)

{
  if (param_2 != 0) {
    dsp_stub();
    dsp_stub();
    dsp_stub();
    dsp_stub();
                    /* WARNING: Bad instruction - Truncating control flow here */
    halt_baddata();
  }
  return;
}

