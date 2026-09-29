
float FUN_0053937c(float param_1,float param_2)

{
  byte bVar1;
  float fVar2;
  float fVar3;
  
  fVar2 = param_2;
  if ((int)((uint)(param_1 < param_2) << 0x1f) < 0) {
    fVar2 = param_1;
    param_1 = param_2;
  }
  bVar1 = 0;
  while( true ) {
    fVar3 = fVar2;
    if (0xf < bVar1) {
      return -1.0;
    }
    if ((int)((uint)(fVar3 < DAT_00539668) << 0x1f) < 0) break;
    fVar2 = (float)FUN_0043a5a0(param_1 / fVar3);
    bVar1 = bVar1 + 1;
    fVar2 = param_1 - fVar2 * fVar3;
    param_1 = fVar3;
  }
  return param_1;
}

