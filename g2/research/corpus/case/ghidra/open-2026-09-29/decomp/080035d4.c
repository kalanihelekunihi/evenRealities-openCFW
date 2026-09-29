
void peripheral_transaction_guard(void)

{
  int iVar1;
  
  iVar1 = DAT_080035ec;
  if (*(char *)(DAT_080035ec + 1) == '\0') {
    *(undefined1 *)(DAT_080035ec + 1) = 1;
    case_serial_read_70();
    *(undefined1 *)(iVar1 + 1) = 0;
  }
  return;
}

