
void FUN_004d15e8(code *UNRECOVERED_JUMPTABLE,undefined4 *param_2)

{
  param_2[3] = param_2[3] + 1;
                    /* WARNING: Could not recover jumptable at 0x004d15f8. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)(*param_2,0,1);
  return;
}

