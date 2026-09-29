
void FUN_0800c014(void)

{
  int iVar1;
  
  if (*DAT_0800c02c != 0) {
    iVar1 = *DAT_0800c02c + -1;
    *DAT_0800c02c = iVar1;
    if (iVar1 == 0) {
      enableIRQinterrupts();
    }
    return;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

