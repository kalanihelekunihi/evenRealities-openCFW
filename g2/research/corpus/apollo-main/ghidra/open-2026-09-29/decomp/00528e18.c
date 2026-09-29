
uint ft_trig_prenorm(uint *param_1)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  uVar4 = *param_1;
  uVar5 = param_1[1];
  uVar2 = uVar4;
  if ((int)uVar4 < 0) {
    uVar2 = -uVar4;
  }
  uVar3 = uVar5;
  if ((int)uVar5 < 0) {
    uVar3 = -uVar5;
  }
  iVar1 = FT_MSB(uVar2 | uVar3);
  if (iVar1 < 0x1e) {
    uVar2 = 0x1d - iVar1;
    *param_1 = uVar4 << (uVar2 & 0xff);
    param_1[1] = uVar5 << (uVar2 & 0xff);
  }
  else {
    uVar2 = iVar1 - 0x1d;
    *param_1 = (int)uVar4 >> (uVar2 & 0xff);
    param_1[1] = (int)uVar5 >> (uVar2 & 0xff);
    uVar2 = -uVar2;
  }
  return uVar2;
}

