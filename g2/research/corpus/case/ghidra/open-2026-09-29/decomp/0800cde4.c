
bool case_critical_read_flag40(int param_1)

{
  byte bVar1;
  
  if (param_1 != 0) {
    FUN_0800bffc();
    bVar1 = *(byte *)(param_1 + 0x28);
    FUN_0800c014();
    return (bVar1 & 1) != 0;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

