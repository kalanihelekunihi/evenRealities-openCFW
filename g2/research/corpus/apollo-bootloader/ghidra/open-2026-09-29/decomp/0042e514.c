
undefined4 terminal_mode_42e514(char param_1)

{
  if (param_1 == '\0') {
    *DAT_0042e534 = 0xd4;
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if (param_1 != '\x01') {
    return 6;
  }
  *DAT_0042e538 = 0x1b;
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

