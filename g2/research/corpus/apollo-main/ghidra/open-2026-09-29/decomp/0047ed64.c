
undefined4 FUN_0047ed64(undefined4 *param_1)

{
  undefined4 uVar1;
  
  ulSetInterruptMask();
  uVar1 = *param_1;
  vClearInterruptMask();
  return uVar1;
}

