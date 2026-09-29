
/* WARNING: Control flow encountered bad instruction data */

void FUN_1000efd4(short *param_1,int param_2,undefined4 param_3,undefined2 *param_4)

{
  short sVar1;
  short sVar2;
  
  if (param_2 != 1) {
    dsp_stub();
    dsp_stub();
    dsp_stub();
    dsp_stub();
                    /* WARNING: Bad instruction - Truncating control flow here */
    halt_baddata();
  }
  sVar1 = *param_1;
  sVar2 = param_1[1];
  param_4[2] = (short)(((longlong)(int)sVar1 - (longlong)(int)sVar2) / 2);
  param_4[3] = 0;
  *param_4 = (short)(((longlong)(int)sVar1 + (longlong)(int)sVar2) / 2);
  param_4[1] = 0;
  return;
}

