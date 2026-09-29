
int FUN_0800c5d0(int param_1,int param_2,int param_3,int param_4)

{
  if (param_1 == 0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if (param_4 == 0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if ((param_3 != 0) && (param_2 == 0)) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if ((param_3 == 0) && (param_2 != 0)) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  *(undefined1 *)(param_4 + 0x46) = 1;
  FUN_0800ae74();
  return param_4;
}

