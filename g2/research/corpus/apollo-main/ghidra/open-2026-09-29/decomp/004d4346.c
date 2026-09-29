
undefined8 FUN_004d4346(undefined4 param_1)

{
  uint in_fpscr;
  undefined8 uVar1;
  
  uVar1 = VectorUnsignedToFloat(param_1,(byte)(in_fpscr >> 0x16) & 3);
  return uVar1;
}

