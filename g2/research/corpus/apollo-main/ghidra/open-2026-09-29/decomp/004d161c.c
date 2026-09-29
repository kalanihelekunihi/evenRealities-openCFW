
void FUN_004d161c(code *UNRECOVERED_JUMPTABLE,undefined4 *param_2,int param_3)

{
  param_2[3] = param_2[3] + -1;
  if (param_3 != -1) {
                    /* WARNING: Could not recover jumptable at 0x004d1632. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (*UNRECOVERED_JUMPTABLE)(*param_2,param_3,0);
    return;
  }
  return;
}

