
void FUN_00541ba8(undefined4 param_1)

{
  int iVar1;
  
  iVar1 = FUN_004d43a4();
                    /* WARNING: Could not recover jumptable at 0x00541bba. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (**(code **)(iVar1 + 0x10))(param_1);
  return;
}

