
int nvdbSysDtYear(byte param_1)

{
  int iVar1;
  
  if (param_1 - 0x41 < 0x1a) {
    iVar1 = param_1 + 0x7a7;
  }
  else {
    iVar1 = 0;
  }
  return iVar1;
}

