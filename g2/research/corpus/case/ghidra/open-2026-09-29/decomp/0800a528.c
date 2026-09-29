
bool case_select_mask(void)

{
  int iVar1;
  undefined4 uVar2;
  
  if (*DAT_0800a548 == '\0') {
    uVar2 = 0x10;
  }
  else {
    uVar2 = 8;
  }
  iVar1 = case_register_any_bits(DAT_0800a54c,uVar2);
  return iVar1 != 0;
}

