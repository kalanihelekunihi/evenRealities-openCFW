
void FUN_0800c178(int param_1,undefined4 param_2)

{
  if (param_1 != 0) {
    FUN_0800bfb0(param_1,*DAT_0800c198 + 0x18);
    FUN_0800abb0(param_2,1);
    return;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

