
void FUN_0047e06a(void)

{
  int *piVar1;
  
  piVar1 = DAT_0047e2c0;
  if (*DAT_0047e2c0 != 0) {
    file_close(*DAT_0047e2c0);
    *piVar1 = 0;
  }
  return;
}

