
undefined4 FUN_004ff2b8(undefined4 param_1,undefined4 *param_2,uint param_3,undefined4 param_4)

{
  uint in_fpscr;
  float fVar1;
  uint uVar2;
  undefined4 uVar3;
  float fVar4;
  float fVar5;
  
  uVar3 = DAT_004ff490;
  if ((param_3 != 0) && (param_2 != (undefined4 *)0x0)) {
    if (param_3 == 1) {
      uVar3 = *param_2;
    }
    else {
      fVar1 = (float)VectorSignedToFloat(param_1,(byte)(in_fpscr >> 0x16) & 3);
      fVar5 = (float)VectorUnsignedToFloat(param_3,(byte)(in_fpscr >> 0x16) & 3);
      fVar4 = (float)VectorSignedToFloat(param_4,(byte)(in_fpscr >> 0x16) & 3);
      uVar2 = (uint)((fVar1 * fVar5) / fVar4);
      if (param_3 <= uVar2) {
        uVar2 = param_3 - 1;
      }
      uVar3 = param_2[uVar2];
    }
  }
  return uVar3;
}

