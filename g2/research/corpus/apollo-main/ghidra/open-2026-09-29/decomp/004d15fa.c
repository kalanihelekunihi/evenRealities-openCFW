
undefined4 FUN_004d15fa(code *UNRECOVERED_JUMPTABLE,undefined4 *param_2)

{
  undefined4 uVar1;
  int iVar2;
  
  iVar2 = param_2[4];
  param_2[4] = iVar2 + -1;
  param_2[3] = param_2[3] + 1;
  if (-1 < iVar2 + -1) {
                    /* WARNING: Could not recover jumptable at 0x004d1614. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    uVar1 = (*UNRECOVERED_JUMPTABLE)(*param_2,0,1);
    return uVar1;
  }
  return 0xffffffff;
}

