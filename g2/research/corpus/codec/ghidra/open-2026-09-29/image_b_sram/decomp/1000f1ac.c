
/* WARNING: Control flow encountered bad instruction data */

void FUN_1000f1ac(undefined4 param_1,undefined4 *param_2,uint param_3)

{
  if (param_3 >> 2 != 0) {
    dsp_stub();
    *param_2 = param_1;
    param_2[1] = param_1;
                    /* WARNING: Bad instruction - Truncating control flow here */
    halt_baddata();
  }
  if ((param_3 & 3) != 0) {
    *(short *)param_2 = (short)param_1;
                    /* WARNING: Bad instruction - Truncating control flow here */
    halt_baddata();
  }
  return;
}

