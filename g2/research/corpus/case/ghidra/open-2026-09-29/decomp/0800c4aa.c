
undefined4 * FUN_0800c4aa(undefined4 *param_1)

{
  if (param_1 != (undefined4 *)0x0) {
    *param_1 = 0;
    FUN_0800bf94(param_1 + 1);
    *(undefined1 *)(param_1 + 7) = 1;
    return param_1;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

