
void FUN_0800af30(undefined4 param_1,int param_2,int param_3,undefined4 param_4,undefined4 param_5,
                 undefined4 *param_6)

{
  if (param_2 != 0) {
    if (param_6 != (undefined4 *)0x0) {
      FUN_0800ac84();
      *param_6 = param_1;
      param_6[6] = param_2;
      param_6[7] = param_4;
      param_6[8] = param_5;
      FUN_0800bfaa(param_6 + 1);
      if (param_3 != 0) {
        *(byte *)(param_6 + 10) = *(byte *)(param_6 + 10) | 4;
      }
    }
    return;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

