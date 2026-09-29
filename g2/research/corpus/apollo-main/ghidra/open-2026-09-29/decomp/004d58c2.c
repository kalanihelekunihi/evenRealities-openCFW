
void FUN_004d58c2(undefined4 param_1)

{
  int iVar1;
  
  iVar1 = FUN_004d43a4();
                    /* WARNING: Could not recover jumptable at 0x004d58d4. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (**(code **)(iVar1 + 0x28))(param_1);
  return;
}

