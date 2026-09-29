
void WsfCsExit(void)

{
  char *pcVar1;
  
  pcVar1 = DAT_0052bab8;
  *DAT_0052bab8 = *DAT_0052bab8 + -1;
  if (*pcVar1 == '\0') {
    enableIRQinterrupts();
  }
  return;
}

