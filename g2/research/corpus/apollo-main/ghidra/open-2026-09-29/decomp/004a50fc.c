
int semantic_normalize_heading(int param_1)

{
  int iVar1;
  
  iVar1 = param_1 + 0x5a;
  if (iVar1 < 0) {
    iVar1 = param_1 + 0x1c2;
  }
  return iVar1 % 0x168;
}

