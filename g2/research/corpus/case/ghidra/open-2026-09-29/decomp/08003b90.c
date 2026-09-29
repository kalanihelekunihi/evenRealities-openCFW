
undefined4 peripheral_status_probe(void)

{
  int iVar1;
  
  iVar1 = case_start_context_transfer(DAT_08003bac,DAT_08003ba8,1);
  if (iVar1 != 0) {
    return 0;
  }
  return 1;
}

