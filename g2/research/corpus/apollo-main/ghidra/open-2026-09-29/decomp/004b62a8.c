
int dmConnCcbById(int param_1)

{
  int iVar1;
  
  if (*(char *)((param_1 - 1U & 0xff) * 0x30 + DAT_004b6520 + 0x16) == '\0') {
    iVar1 = 0;
  }
  else {
    iVar1 = DAT_004b6520 + (param_1 - 1U & 0xff) * 0x30;
  }
  return iVar1;
}

