
undefined4 FUN_004d38ea(uint param_1,undefined4 param_2,uint param_3,undefined4 *param_4)

{
  uint in_fpscr;
  float fVar1;
  undefined4 uVar2;
  float fVar3;
  
  fVar1 = (float)VectorUnsignedToFloat(param_2,(byte)(in_fpscr >> 0x16) & 3);
  fVar3 = (float)VectorUnsignedToFloat
                           (param_1 / (uint)(1 << (param_3 & 0xff)),(byte)(in_fpscr >> 0x16) & 3);
  uVar2 = VectorFloatToUnsignedFixed(fVar1 / fVar3,0x20,0xf);
  *param_4 = uVar2;
  return 0;
}

