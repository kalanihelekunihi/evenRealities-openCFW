
undefined8 FUN_004515b0(undefined4 *param_1)

{
  uint in_fpscr;
  undefined4 uVar1;
  undefined4 uVar2;
  
  uVar1 = VectorSignedToFloat(*param_1,(byte)(in_fpscr >> 0x16) & 3);
  uVar2 = VectorSignedToFloat(param_1[1],(byte)(in_fpscr >> 0x16) & 3);
  return CONCAT44(uVar2,uVar1);
}

