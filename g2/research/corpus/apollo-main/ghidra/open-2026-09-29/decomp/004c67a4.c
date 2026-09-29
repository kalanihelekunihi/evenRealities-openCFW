
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void device_mgr_fn_004c67a4(char param_1)

{
  char *pcVar1;
  
  pcVar1 = _DAT_004c6cac;
  if (param_1 == '\0') {
    if (*_DAT_004c6cac != '\0') {
      FUN_0053a5be(7,0);
      *pcVar1 = '\0';
    }
  }
  else if (*_DAT_004c6cac == '\0') {
    FUN_0053a5be(7,1);
    *pcVar1 = '\x01';
  }
  return;
}

