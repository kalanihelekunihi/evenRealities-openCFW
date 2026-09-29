
void FUN_0800c128(int param_1)

{
  int iVar1;
  undefined4 extraout_r2;
  
  iVar1 = 0;
  if (param_1 != 0) {
    if (*(int *)(DAT_0800c158 + 0x30) != 0) {
      disableIRQinterrupts();
      do {
                    /* WARNING: Do nothing block with infinite loop */
      } while( true );
    }
    FUN_0800c380();
    FUN_0800abb0(extraout_r2,0);
    iVar1 = FUN_0800cc0c();
  }
  if (iVar1 == 0) {
    FUN_0800c0a0();
  }
  return;
}

