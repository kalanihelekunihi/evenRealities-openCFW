
int gx8002_padmux_set(uint param_1,uint param_2)

{
  int iVar1;
  uint *puVar2;
  
  if (param_1 < 0x21) {
    puVar2 = (uint *)(((int)param_1 >> 3) * 4 + DAT_1020662c);
    iVar1 = (param_1 & 7) << 2;
    *puVar2 = (param_2 & 0xf) << iVar1 | *puVar2 & ~(0xf << iVar1);
    iVar1 = gx8002_padmux_check();
    iVar1 = -(uint)(iVar1 != 0);
  }
  else {
    iVar1 = -1;
  }
  return iVar1;
}

