
void gx8002_aout_set_lodac(undefined4 param_1)

{
  uint uVar1;
  
  uRam00000028 = uRam00000028 & 0xfffffffd | 1;
  uVar1 = ((uRam00000004 & 0x3f) >> 4) - 1;
  if (uVar1 < 7) {
                    /* WARNING: Could not recover jumptable at 0x10204b98. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (*(code *)(*(uint *)(iRam10204b9c + uVar1 * 4) & 0xfffffffe))(param_1,uVar1,0);
    return;
  }
  uRam00000028 = 0x2385;
  return;
}

