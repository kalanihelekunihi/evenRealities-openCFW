
void peripheral_init_retry(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = 0;
  do {
    iVar1 = case_start_validated();
    if (2 < iVar2) {
      return;
    }
    iVar2 = iVar2 + 1;
  } while (iVar1 != 0);
  return;
}

