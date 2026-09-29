
undefined4 FUN_005c5cf0(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  byte bVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  short sVar14;
  short sVar15;
  uint in_fpscr;
  float fVar16;
  undefined1 auStack_90 [8];
  int local_88;
  int local_80;
  float local_74;
  float local_70;
  float local_6c;
  float local_68;
  undefined1 auStack_50 [16];
  undefined1 auStack_40 [16];
  
  cVar1 = FUN_00450bcc(auStack_40,param_1 + 0x14,param_2 + 0x18);
  if (cVar1 != '\0') {
    FUN_00439c04(auStack_50,param_2 + 0x18,0x10);
    FUN_00439c04(param_2 + 0x18,auStack_40,0x10);
    iVar3 = FUN_005c579c(param_1,0);
    iVar4 = FUN_005c5772(param_1,0);
    iVar5 = FUN_005c575e(param_1,0);
    iVar6 = FUN_0043fe16(param_1);
    iVar7 = FUN_0043fe70(param_1);
    FUN_005c6fbc(auStack_90);
    local_80 = param_2;
    FUN_00452b0e(param_1,0,auStack_90);
    bVar2 = FUN_005c5790(param_1,0);
    iVar8 = FUN_005c579c(param_1,0);
    iVar9 = FUN_005c57a6(param_1,0);
    iVar10 = FUN_0044e586(param_1);
    iVar11 = FUN_0044e4aa(param_1);
    if (*(int *)(param_1 + 0x68) != 0) {
      iVar12 = *(int *)(param_1 + 0x18);
      local_74 = (float)VectorSignedToFloat(*(undefined4 *)(param_1 + 0x14),
                                            (byte)(in_fpscr >> 0x16) & 3);
      local_6c = (float)VectorSignedToFloat(*(undefined4 *)(param_1 + 0x1c),
                                            (byte)(in_fpscr >> 0x16) & 3);
      sVar15 = 0;
      sVar14 = (short)*(undefined4 *)(param_1 + 0x68);
      if ((2 < bVar2) && (0 < iVar8)) {
        if ((iVar9 << 0x1e < 0) && (iVar13 = FUN_005c575e(param_1,0), iVar13 == 0)) {
          sVar15 = 1;
        }
        if ((iVar9 << 0x1f < 0) && (iVar13 = FUN_005c5768(param_1,0), iVar13 == 0)) {
          sVar14 = sVar14 + -1;
        }
      }
      for (; sVar15 < sVar14; sVar15 = sVar15 + 1) {
        fVar16 = (float)VectorUnsignedToFloat
                                  ((uint)(sVar15 * iVar7) / (*(int *)(param_1 + 0x68) - 1U),
                                   (byte)(in_fpscr >> 0x16) & 3);
        local_70 = (float)VectorSignedToFloat((iVar3 + iVar5 + iVar12) - iVar11,
                                              (byte)(in_fpscr >> 0x16) & 3);
        local_70 = local_70 + fVar16;
        local_88 = (int)sVar15;
        local_68 = local_70;
        FUN_005c6fea(param_2,auStack_90);
      }
    }
    if (*(int *)(param_1 + 0x6c) != 0) {
      iVar5 = *(int *)(param_1 + 0x14);
      local_70 = (float)VectorSignedToFloat(*(undefined4 *)(param_1 + 0x18),
                                            (byte)(in_fpscr >> 0x16) & 3);
      local_68 = (float)VectorSignedToFloat(*(undefined4 *)(param_1 + 0x20),
                                            (byte)(in_fpscr >> 0x16) & 3);
      sVar15 = 0;
      sVar14 = (short)*(undefined4 *)(param_1 + 0x6c);
      if ((2 < bVar2) && (0 < iVar8)) {
        if ((iVar9 << 0x1d < 0) && (iVar7 = FUN_005c5772(param_1,0), iVar7 == 0)) {
          sVar15 = 1;
        }
        if ((iVar9 << 0x1c < 0) && (iVar7 = FUN_005c577c(param_1,0), iVar7 == 0)) {
          sVar14 = sVar14 + -1;
        }
      }
      for (; sVar15 < sVar14; sVar15 = sVar15 + 1) {
        fVar16 = (float)VectorUnsignedToFloat
                                  ((uint)(sVar15 * iVar6) / (*(int *)(param_1 + 0x6c) - 1U),
                                   (byte)(in_fpscr >> 0x16) & 3);
        local_74 = (float)VectorSignedToFloat((iVar3 + iVar4 + iVar5) - iVar10,
                                              (byte)(in_fpscr >> 0x16) & 3);
        local_74 = local_74 + fVar16;
        local_88 = (int)sVar15;
        local_6c = local_74;
        FUN_005c6fea(param_2,auStack_90);
      }
    }
    FUN_00439c04(param_2 + 0x18,auStack_50,0x10);
  }
  return param_4;
}

