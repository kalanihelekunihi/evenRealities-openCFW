
undefined4 FUN_005394e0(float param_1,float param_2,undefined1 *param_3,short *param_4,int *param_5)

{
  uint uVar1;
  undefined4 uVar2;
  uint in_fpscr;
  float fVar3;
  float fVar4;
  int iVar5;
  
  fVar3 = (float)FUN_00577d40(10.0 / (param_2 / param_1),param_2,DAT_00539784,0);
  if ((fVar3 < DAT_00539668) ||
     (uVar1 = in_fpscr & 0xfffffff | (uint)(fVar3 < DAT_00539780) << 0x1f,
     SUB41(uVar1 >> 0x1f,0) == (NAN(fVar3) || NAN(DAT_00539780)))) {
    uVar2 = 0;
  }
  else {
    iVar5 = (uint)(0.0 < fVar3) * (int)fVar3;
    fVar3 = (float)VectorUnsignedToFloat(iVar5,(byte)(uVar1 >> 0x16) & 3);
    fVar3 = fVar3 * (param_2 / param_1);
    fVar4 = (float)FUN_00577c3c(fVar3,0x3f800000);
    fVar4 = (float)FUN_00577d08(fVar4 * DAT_00539788);
    fVar3 = (float)FUN_0043a5a0(fVar3);
    if (((int)((uint)(fVar3 < 10.0) << 0x1f) < 0) || (DAT_0053978c <= fVar3)) {
      uVar2 = 0;
    }
    else {
      fVar3 = (float)FUN_0043a5a0();
      *param_3 = (char)iVar5;
      *param_4 = (ushort)(0.0 < fVar3) * (short)(int)fVar3;
      *param_5 = (uint)(0.0 < fVar4) * (int)fVar4;
      uVar2 = 1;
    }
  }
  return uVar2;
}

