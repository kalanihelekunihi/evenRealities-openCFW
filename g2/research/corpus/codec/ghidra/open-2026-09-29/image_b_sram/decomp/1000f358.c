
/* WARNING: Control flow encountered bad instruction data */

void FUN_1000f358(int param_1,uint param_2,undefined4 param_3)

{
  if (param_2 >> 1 != 0) {
                    /* WARNING: Bad instruction - Truncating control flow here */
    halt_baddata();
  }
  FUN_1000f610(param_1,0,param_3,2);
  FUN_1000f610(param_2 * 2 + param_1,param_2 >> 1,param_3,2);
  if (param_2 >> 1 != 0) {
    dsp_stub();
                    /* WARNING: Bad instruction - Truncating control flow here */
    halt_baddata();
  }
  return;
}

