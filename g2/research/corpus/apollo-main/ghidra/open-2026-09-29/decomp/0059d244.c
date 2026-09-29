
void frexpf(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *extraout_r3;
  code *UNRECOVERED_JUMPTABLE;
  undefined8 uVar1;
  
  uVar1 = _internal_frexpf_bits(param_1,param_3,param_4,param_2);
  *extraout_r3 = (int)((ulonglong)uVar1 >> 0x20);
                    /* WARNING: Could not recover jumptable at 0x0059d256. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)((int)uVar1);
  return;
}

