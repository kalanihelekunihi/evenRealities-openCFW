
/* WARNING: Control flow encountered bad instruction data */

void FUN_1000f180(undefined4 *param_1,undefined4 *param_2,uint param_3)

{
  undefined4 in_r12;
  undefined4 in_r13;
  
  if (param_3 >> 2 != 0) {
    dsp_stub();
    *param_2 = in_r12;
    param_2[1] = in_r13;
                    /* WARNING: Bad instruction - Truncating control flow here */
    halt_baddata();
  }
  if ((param_3 & 3) != 0) {
    *(short *)param_2 = (short)*param_1;
                    /* WARNING: Bad instruction - Truncating control flow here */
    halt_baddata();
  }
  return;
}

