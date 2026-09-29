
int ft_trig_downscale(uint param_1)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  iVar2 = 1;
  if ((int)param_1 < 0) {
    param_1 = -param_1;
    iVar2 = -1;
  }
  uVar4 = (param_1 >> 0x10) * 0x5b16;
  uVar3 = uVar4 + (param_1 & 0xffff) * 0xdbd9;
  iVar1 = (param_1 >> 0x10) * 0xdbd9 + (uint)(uVar3 < uVar4) * 0x10000 + (uVar3 >> 0x10);
  uVar4 = uVar3 * 0x10000 + (param_1 & 0xffff) * 0x5b16;
  if (uVar4 < uVar3 * 0x10000) {
    iVar1 = iVar1 + 1;
  }
  if (uVar4 + 0x40000000 < 0x40000000) {
    iVar1 = iVar1 + 1;
  }
  if (iVar2 < 0) {
    iVar1 = -iVar1;
  }
  return iVar1;
}

