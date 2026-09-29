
void left_channel_transaction_guard(void)

{
  int iVar1;
  
  iVar1 = DAT_080039e0;
  if (*(char *)(DAT_080039e0 + 1) == '\0') {
    *(undefined1 *)(DAT_080039e0 + 1) = 1;
    case_serial_write_pair_200();
    *(undefined1 *)(iVar1 + 1) = 0;
  }
  return;
}

