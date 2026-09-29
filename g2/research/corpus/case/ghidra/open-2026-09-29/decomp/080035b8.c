
void case_run_guarded(void)

{
  int iVar1;
  
  iVar1 = DAT_080035d0;
  if (*(char *)(DAT_080035d0 + 1) == '\0') {
    *(undefined1 *)(DAT_080035d0 + 1) = 1;
    case_serial_read_200();
    *(undefined1 *)(iVar1 + 1) = 0;
  }
  return;
}

