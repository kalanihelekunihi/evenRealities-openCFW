
undefined4 case_critical_read_word28(int param_1)

{
  undefined4 uVar1;
  
  if (param_1 != 0) {
    FUN_0800bffc();
    uVar1 = *(undefined4 *)(param_1 + 0x1c);
    FUN_0800c014();
    return uVar1;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

