
int FUN_005c1138(float param_1,float param_2,int param_3,int param_4,ushort param_5,int param_6,
                char param_7,int *param_8)

{
  short sVar1;
  uint uVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int local_28;
  short sVar2;
  
  uVar6 = (uint)param_5;
  iVar8 = (int)param_1;
  iVar9 = (int)param_2;
  local_28 = param_6;
  if (iVar9 == iVar8 + 0x168) {
    *param_8 = param_3 - uVar6;
    param_8[1] = param_4 - uVar6;
    param_8[2] = uVar6 + param_3;
    param_8[3] = uVar6 + param_4;
  }
  else {
    if (0x168 < iVar8) {
      iVar8 = iVar8 + -0x168;
    }
    if (0x168 < iVar9) {
      iVar9 = iVar9 + -0x168;
    }
    iVar5 = (uint)param_5 - param_6;
    if (param_7 == '\0') {
      iVar7 = 0;
    }
    else {
      iVar7 = param_6 / 2 + 1;
    }
    uVar3 = iVar8 / 0x5a;
    uVar4 = iVar9 / 0x5a;
    if ((uVar3 & 0xff) == 4) {
      uVar3 = 3;
    }
    if ((uVar4 & 0xff) == 4) {
      uVar4 = 3;
    }
    sVar1 = (short)iVar8;
    sVar2 = (short)iVar9;
    if (((uVar3 & 0xff) == (uVar4 & 0xff)) && (iVar8 <= iVar9)) {
      if ((uVar3 & 0xff) == 0) {
        iVar8 = FUN_004885f0((int)sVar1);
        param_8[1] = (param_4 + (iVar5 * iVar8 >> 0xf)) - iVar7;
        iVar8 = FUN_004885f0((int)(short)(sVar1 + 0x5a));
        param_8[2] = iVar7 + param_3 + ((int)(uVar6 * iVar8) >> 0xf);
        iVar8 = FUN_004885f0((int)sVar2);
        param_8[3] = iVar7 + param_4 + ((int)(uVar6 * iVar8) >> 0xf);
        iVar8 = FUN_004885f0((int)(short)(sVar2 + 0x5a));
        *param_8 = (param_3 + (iVar5 * iVar8 >> 0xf)) - iVar7;
      }
      else if ((uVar3 & 0xff) == 1) {
        iVar8 = FUN_004885f0((int)sVar1);
        param_8[3] = iVar7 + param_4 + ((int)(uVar6 * iVar8) >> 0xf);
        iVar8 = FUN_004885f0((int)(short)(sVar1 + 0x5a));
        param_8[2] = iVar7 + param_3 + (iVar5 * iVar8 >> 0xf);
        iVar8 = FUN_004885f0((int)sVar2);
        param_8[1] = (param_4 + (iVar5 * iVar8 >> 0xf)) - iVar7;
        iVar8 = FUN_004885f0((int)(short)(sVar2 + 0x5a));
        *param_8 = (param_3 + ((int)(uVar6 * iVar8) >> 0xf)) - iVar7;
      }
      else if ((uVar3 & 0xff) == 2) {
        iVar8 = FUN_004885f0((int)(short)(sVar1 + 0x5a));
        *param_8 = (param_3 + ((int)(uVar6 * iVar8) >> 0xf)) - iVar7;
        iVar8 = FUN_004885f0((int)sVar1);
        param_8[3] = iVar7 + param_4 + (iVar5 * iVar8 >> 0xf);
        iVar8 = FUN_004885f0((int)sVar2);
        param_8[1] = (param_4 + ((int)(uVar6 * iVar8) >> 0xf)) - iVar7;
        iVar8 = FUN_004885f0((int)(short)(sVar2 + 0x5a));
        param_8[2] = iVar7 + param_3 + (iVar5 * iVar8 >> 0xf);
      }
      else if ((uVar3 & 0xff) == 3) {
        iVar8 = FUN_004885f0((int)(short)(sVar1 + 0x5a));
        *param_8 = (param_3 + (iVar5 * iVar8 >> 0xf)) - iVar7;
        iVar8 = FUN_004885f0((int)sVar1);
        param_8[1] = (param_4 + ((int)(uVar6 * iVar8) >> 0xf)) - iVar7;
        iVar8 = FUN_004885f0((int)(short)(sVar2 + 0x5a));
        param_8[2] = iVar7 + param_3 + ((int)(uVar6 * iVar8) >> 0xf);
        iVar8 = FUN_004885f0((int)sVar2);
        param_8[3] = iVar7 + param_4 + (iVar5 * iVar8 >> 0xf);
      }
    }
    else if (((uVar3 & 0xff) == 0) && ((uVar4 & 0xff) == 1)) {
      iVar8 = FUN_004885f0((int)(short)(sVar2 + 0x5a));
      *param_8 = (param_3 + ((int)(uVar6 * iVar8) >> 0xf)) - iVar7;
      local_28 = FUN_004885f0((int)sVar2);
      iVar8 = FUN_004885f0((int)sVar1);
      if (local_28 < iVar8) {
        iVar8 = FUN_004885f0((int)sVar2);
      }
      else {
        iVar8 = FUN_004885f0((int)sVar1);
      }
      param_8[1] = (param_4 + (iVar5 * iVar8 >> 0xf)) - iVar7;
      iVar8 = FUN_004885f0((int)(short)(sVar1 + 0x5a));
      param_8[2] = iVar7 + param_3 + ((int)(uVar6 * iVar8) >> 0xf);
      param_8[3] = iVar7 + uVar6 + param_4;
    }
    else if (((uVar3 & 0xff) == 1) && ((uVar4 & 0xff) == 2)) {
      *param_8 = (param_3 - uVar6) - iVar7;
      iVar8 = FUN_004885f0((int)sVar2);
      param_8[1] = (param_4 + ((int)(uVar6 * iVar8) >> 0xf)) - iVar7;
      local_28 = FUN_004885f0((int)(short)(sVar2 + 0x5a));
      iVar8 = FUN_004885f0((int)(short)(sVar1 + 0x5a));
      if (local_28 < iVar8) {
        iVar8 = FUN_004885f0((int)(short)(sVar1 + 0x5a));
      }
      else {
        iVar8 = FUN_004885f0((int)(short)(sVar2 + 0x5a));
      }
      param_8[2] = iVar7 + param_3 + (iVar5 * iVar8 >> 0xf);
      iVar8 = FUN_004885f0((int)sVar1);
      param_8[3] = iVar7 + param_4 + ((int)(uVar6 * iVar8) >> 0xf);
    }
    else if (((uVar3 & 0xff) == 2) && ((uVar4 & 0xff) == 3)) {
      iVar8 = FUN_004885f0((int)(short)(sVar1 + 0x5a));
      *param_8 = (param_3 + ((int)(uVar6 * iVar8) >> 0xf)) - iVar7;
      param_8[1] = (param_4 - uVar6) - iVar7;
      iVar8 = FUN_004885f0((int)(short)(sVar2 + 0x5a));
      param_8[2] = iVar7 + param_3 + ((int)(uVar6 * iVar8) >> 0xf);
      iVar8 = FUN_004885f0((int)sVar1);
      iVar9 = FUN_004885f0((int)sVar2);
      if (iVar5 * iVar8 < iVar5 * iVar9) {
        iVar8 = FUN_004885f0((int)sVar2);
      }
      else {
        iVar8 = FUN_004885f0((int)sVar1);
      }
      param_8[3] = iVar7 + param_4 + (iVar5 * iVar8 >> 0xf);
    }
    else if (((uVar3 & 0xff) == 3) && ((uVar4 & 0xff) == 0)) {
      local_28 = FUN_004885f0((int)(short)(sVar2 + 0x5a));
      iVar8 = FUN_004885f0((int)(short)(sVar1 + 0x5a));
      if (local_28 < iVar8) {
        iVar8 = FUN_004885f0((int)(short)(sVar2 + 0x5a));
      }
      else {
        iVar8 = FUN_004885f0((int)(short)(sVar1 + 0x5a));
      }
      *param_8 = (param_3 + (iVar5 * iVar8 >> 0xf)) - iVar7;
      iVar8 = FUN_004885f0((int)sVar1);
      param_8[1] = (param_4 + ((int)(uVar6 * iVar8) >> 0xf)) - iVar7;
      param_8[2] = iVar7 + uVar6 + param_3;
      iVar8 = FUN_004885f0((int)sVar2);
      param_8[3] = iVar7 + param_4 + ((int)(uVar6 * iVar8) >> 0xf);
    }
    else {
      *param_8 = param_3 - uVar6;
      param_8[1] = param_4 - uVar6;
      param_8[2] = uVar6 + param_3;
      param_8[3] = uVar6 + param_4;
    }
  }
  return local_28;
}

