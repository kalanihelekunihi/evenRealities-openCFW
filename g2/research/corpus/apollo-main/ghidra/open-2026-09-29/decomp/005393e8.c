
undefined4 FUN_005393e8(float param_1,float param_2,byte *param_3,ushort *param_4)

{
  uint uVar1;
  float fVar2;
  uint uVar3;
  float fVar4;
  uint uVar5;
  
  fVar2 = (float)FUN_0053937c(param_2,param_1);
  fVar4 = DAT_0053966c;
  if (-1 < (int)((uint)(fVar2 < DAT_00539668) << 0x1f)) {
    param_2 = param_2 / fVar2;
    param_1 = param_1 / fVar2;
    fVar2 = (float)FUN_00577c3c(param_2,0x3f800000);
    if ((fVar2 < fVar4) && (fVar2 = (float)FUN_00577d08(param_2), fVar2 < DAT_00539670)) {
      fVar2 = (float)FUN_00577d08(param_2);
      uVar3 = (uint)(0.0 < fVar2) * (int)fVar2;
      fVar2 = (float)FUN_00577c3c(param_1,0x3f800000);
      if ((fVar4 <= fVar2) || (fVar4 = (float)FUN_00577d08(param_1), DAT_00539780 <= fVar4)) {
        return 0;
      }
      fVar4 = (float)FUN_00577d08(param_1);
      uVar5 = (uint)(0.0 < fVar4) * (int)fVar4;
      if (uVar3 < 4) {
        uVar1 = (uVar3 + 3) / uVar3;
        uVar5 = uVar1 * uVar5;
        uVar3 = uVar1 * uVar3;
      }
      if ((uVar5 != 0) && (uVar5 < 0x40)) {
        if (uVar3 - 4 < 0x3bd) {
          *param_3 = (byte)uVar5 & 0x3f;
          *param_4 = (ushort)uVar3 & 0xfff;
          return 1;
        }
        return 0;
      }
      return 0;
    }
  }
  return 0;
}

