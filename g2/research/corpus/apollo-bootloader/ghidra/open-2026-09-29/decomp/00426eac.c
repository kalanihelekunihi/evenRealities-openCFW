
undefined4
float_multiplier_426eac(float param_1,float param_2,undefined1 *param_3,short *param_4,int *param_5)

{
  uint uVar1;
  undefined4 uVar2;
  uint in_fpscr;
  float fVar3;
  float fVar4;
  int iVar5;
  
  fVar3 = (float)ceilf_427dd0(10.0 / (param_2 / param_1),param_2,DAT_00427150,0);
  if ((fVar3 < DAT_00427034) ||
     (uVar1 = in_fpscr & 0xfffffff | (uint)(fVar3 < DAT_0042714c) << 0x1f,
     SUB41(uVar1 >> 0x1f,0) == (NAN(fVar3) || NAN(DAT_0042714c)))) {
    uVar2 = 0;
  }
  else {
    iVar5 = (uint)(0.0 < fVar3) * (int)fVar3;
    fVar3 = (float)VectorUnsignedToFloat(iVar5,(byte)(uVar1 >> 0x16) & 3);
    fVar3 = fVar3 * (param_2 / param_1);
    fVar4 = (float)fmodf_427ccc(fVar3,0x3f800000);
    fVar4 = (float)roundf_427d98(fVar4 * DAT_00427154);
    fVar3 = (float)floorf_427c90(fVar3);
    if (((int)((uint)(fVar3 < 10.0) << 0x1f) < 0) || (DAT_00427158 <= fVar3)) {
      uVar2 = 0;
    }
    else {
      fVar3 = (float)floorf_427c90();
      *param_3 = (char)iVar5;
      *param_4 = (ushort)(0.0 < fVar3) * (short)(int)fVar3;
      *param_5 = (uint)(0.0 < fVar4) * (int)fVar4;
      uVar2 = 1;
    }
  }
  return uVar2;
}

