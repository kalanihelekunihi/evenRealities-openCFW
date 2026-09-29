
int FUN_0050a010(int param_1,int param_2)

{
  uint in_fpscr;
  float fVar1;
  int iVar2;
  float fVar3;
  
  if (param_1 < 1) {
    param_1 = 1;
  }
  else if (200 < param_1) {
    param_1 = 200;
  }
  if (param_2 < 1) {
    param_2 = 1;
  }
  else if (200 < param_2) {
    param_2 = 200;
  }
  fVar3 = (float)VectorSignedToFloat(param_2 + 10,(byte)(in_fpscr >> 0x16) & 3);
  fVar1 = (float)VectorSignedToFloat(400 - (param_1 * 0x140) / 200,(byte)(in_fpscr >> 0x16) & 3);
  iVar2 = (int)(fVar1 * (DAT_0050a090 / fVar3));
  if (iVar2 < 0x50) {
    iVar2 = 0x50;
  }
  else if (400 < iVar2) {
    iVar2 = 400;
  }
  return iVar2;
}

