
uint case_atomic_clear_word(uint *param_1,uint param_2)

{
  uint uVar1;
  
  if (param_1 == (uint *)0x0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if (param_2 >> 0x18 != 0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  FUN_0800bffc();
  uVar1 = *param_1;
  *param_1 = uVar1 & ~param_2;
  FUN_0800c014();
  return uVar1;
}

