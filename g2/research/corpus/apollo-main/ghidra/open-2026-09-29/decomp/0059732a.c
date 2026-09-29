
int td_active_session(void)

{
  int iVar1;
  
  if (*(char *)(DAT_00597c08 + 0xa1d9) == '\0') {
    iVar1 = 0;
  }
  else {
    iVar1 = DAT_00597c08 + 0x9560;
  }
  return iVar1;
}

