
void WsfCsEnter(void)

{
  if (*DAT_0052bab8 == '\0') {
    disableIRQinterrupts();
  }
  *DAT_0052bab8 = *DAT_0052bab8 + '\x01';
  return;
}

