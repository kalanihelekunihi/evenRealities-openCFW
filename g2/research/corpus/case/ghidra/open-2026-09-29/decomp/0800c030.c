
void FUN_0800c030(int param_1)

{
  int iVar1;
  
  iVar1 = DAT_0800c074;
  if (param_1 != 0) {
    if ((*(uint *)(param_1 + -4) & *(uint *)(DAT_0800c074 + 0x14)) == 0) {
      disableIRQinterrupts();
      do {
                    /* WARNING: Do nothing block with infinite loop */
      } while( true );
    }
    if (*(int *)(param_1 + -8) != 0) {
      disableIRQinterrupts();
      do {
                    /* WARNING: Do nothing block with infinite loop */
      } while( true );
    }
    *(uint *)(param_1 + -4) = *(uint *)(param_1 + -4) & ~*(uint *)(DAT_0800c074 + 0x14);
    FUN_0800c380();
    *(int *)(iVar1 + 4) = *(int *)(param_1 + -4) + *(int *)(iVar1 + 4);
    FUN_0800afcc((int *)(param_1 + -8));
    *(int *)(iVar1 + 0x10) = *(int *)(iVar1 + 0x10) + 1;
    FUN_0800cc0c();
  }
  return;
}

