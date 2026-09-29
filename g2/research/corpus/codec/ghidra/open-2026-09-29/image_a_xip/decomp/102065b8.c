
int gx8002_padmux_check(int param_1,uint param_2)

{
  uint uVar1;
  int iVar2;
  
  if ((param_1 < 0) || ((int)param_2 < 0)) {
    iVar2 = -1;
  }
  else {
    uVar1 = padmux_get();
    iVar2 = -(uint)((uVar1 & 0xff) != param_2);
  }
  return iVar2;
}

