
undefined8 __aeabi_idiv(uint param_1,uint param_2)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  undefined4 uVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  bool bVar9;
  bool bVar10;
  bool bVar11;
  bool bVar12;
  bool bVar13;
  
  if (-1 < (int)(param_1 | param_2)) {
    iVar6 = 0;
    if (param_2 <= param_1 >> 1) {
      if (param_2 <= param_1 >> 4) {
        if (param_2 <= param_1 >> 8) {
          if (param_1 >> 0xc < param_2) goto LAB_0000a846;
          if (param_2 <= param_1 >> 0x10) {
            iVar6 = -0x1000000;
            uVar7 = param_1 >> 0x10;
            uVar1 = param_2 << 8;
            if (param_2 << 8 <= uVar7) {
              iVar6 = -0x10000;
              uVar1 = param_2 << 0x10;
              if (param_2 << 0x10 == 0) goto LAB_0000a996;
            }
            param_2 = uVar1;
            if (param_1 >> 0xc < param_2) goto LAB_0000a846;
          }
          while( true ) {
            bVar9 = param_2 <= param_1 >> 0xf;
            uVar1 = param_1;
            if (bVar9) {
              uVar1 = param_1 + param_2 * -0x8000;
            }
            bVar13 = param_2 * 0x8000 <= param_1;
            bVar10 = param_2 <= uVar1 >> 0xe;
            uVar2 = uVar1;
            if (bVar10) {
              uVar2 = uVar1 + param_2 * -0x4000;
            }
            bVar11 = param_2 <= uVar2 >> 0xd;
            uVar7 = uVar2;
            if (bVar11) {
              uVar7 = uVar2 + param_2 * -0x2000;
            }
            bVar12 = param_2 <= uVar7 >> 0xc;
            param_1 = uVar7;
            if (bVar12) {
              param_1 = uVar7 + param_2 * -0x1000;
            }
            iVar6 = (((iVar6 * 2 + (uint)(bVar9 && bVar13)) * 2 +
                     (uint)(bVar10 && param_2 * 0x4000 <= uVar1)) * 2 +
                    (uint)(bVar11 && param_2 * 0x2000 <= uVar2)) * 2 +
                    (uint)(bVar12 && param_2 * 0x1000 <= uVar7);
LAB_0000a846:
            bVar9 = param_2 <= param_1 >> 0xb;
            uVar1 = param_1;
            if (bVar9) {
              uVar1 = param_1 + param_2 * -0x800;
            }
            bVar13 = param_2 <= uVar1 >> 10;
            uVar2 = uVar1;
            if (bVar13) {
              uVar2 = uVar1 + param_2 * -0x400;
            }
            bVar10 = param_2 <= uVar2 >> 9;
            uVar7 = uVar2;
            if (bVar10) {
              uVar7 = uVar2 + param_2 * -0x200;
            }
            uVar1 = ((iVar6 * 2 + (uint)(bVar9 && param_2 * 0x800 <= param_1)) * 2 +
                    (uint)(bVar13 && param_2 * 0x400 <= uVar1)) * 2 +
                    (uint)(bVar10 && param_2 * 0x200 <= uVar2);
            bVar9 = param_2 <= uVar7 >> 8;
            param_1 = uVar7;
            if (bVar9) {
              param_1 = uVar7 + param_2 * -0x100;
            }
            bVar9 = bVar9 && param_2 * 0x100 <= uVar7;
            iVar6 = uVar1 * 2 + (uint)bVar9;
            if (!CARRY4(uVar1,uVar1) && !CARRY4(uVar1 * 2,(uint)bVar9)) break;
            param_2 = param_2 >> 8;
          }
        }
        bVar9 = param_2 <= param_1 >> 7;
        uVar1 = param_1;
        if (bVar9) {
          uVar1 = param_1 + param_2 * -0x80;
        }
        bVar13 = param_2 * 0x80 <= param_1;
        bVar10 = param_2 <= uVar1 >> 6;
        uVar2 = uVar1;
        if (bVar10) {
          uVar2 = uVar1 + param_2 * -0x40;
        }
        bVar11 = param_2 <= uVar2 >> 5;
        uVar7 = uVar2;
        if (bVar11) {
          uVar7 = uVar2 + param_2 * -0x20;
        }
        bVar12 = param_2 <= uVar7 >> 4;
        param_1 = uVar7;
        if (bVar12) {
          param_1 = uVar7 + param_2 * -0x10;
        }
        iVar6 = (((iVar6 * 2 + (uint)(bVar9 && bVar13)) * 2 +
                 (uint)(bVar10 && param_2 * 0x40 <= uVar1)) * 2 +
                (uint)(bVar11 && param_2 * 0x20 <= uVar2)) * 2 +
                (uint)(bVar12 && param_2 * 0x10 <= uVar7);
      }
      bVar9 = param_2 <= param_1 >> 3;
      uVar1 = param_1;
      if (bVar9) {
        uVar1 = param_1 + param_2 * -8;
      }
      bVar13 = param_2 * 8 <= param_1;
      bVar10 = param_2 <= uVar1 >> 2;
      uVar2 = uVar1;
      if (bVar10) {
        uVar2 = uVar1 + param_2 * -4;
      }
      bVar11 = param_2 <= uVar2 >> 1;
      param_1 = uVar2;
      if (bVar11) {
        param_1 = uVar2 + param_2 * -2;
      }
      iVar6 = ((iVar6 * 2 + (uint)(bVar9 && bVar13)) * 2 + (uint)(bVar10 && param_2 * 4 <= uVar1)) *
              2 + (uint)(bVar11 && param_2 * 2 <= uVar2);
    }
    uVar1 = param_1 - param_2;
    if (param_2 > param_1) {
      uVar1 = param_1;
    }
    return CONCAT44(uVar1,iVar6 * 2 + (uint)(param_2 <= param_1));
  }
  iVar6 = (int)param_2 >> 0x1f;
  if (-iVar6 != 0) {
    param_2 = -param_2;
  }
  uVar1 = (int)param_1 >> 0x20;
  if (((int)param_1 >> 0x1f & 1U) != 0) {
    param_1 = -param_1;
  }
  uVar1 = uVar1 ^ -iVar6;
  iVar6 = 0;
  uVar7 = (int)uVar1 >> 1;
  uVar2 = param_2;
  if (param_1 >> 4 < param_2) goto LAB_0000a94e;
  if (param_2 <= param_1 >> 8) {
    uVar2 = param_2 << 6;
    iVar6 = -0x4000000;
    uVar8 = param_1 >> 8;
    if (uVar2 <= uVar8) {
      uVar2 = param_2 << 0xc;
      iVar6 = -0x100000;
      if (uVar2 <= uVar8) {
        uVar2 = param_2 << 0x12;
        iVar6 = -0x4000;
        if (uVar2 <= uVar8) {
          uVar2 = param_2 << 0x18;
          if (uVar2 == 0) {
            if ((uVar1 & 1) != 0) {
              param_1 = -param_1;
            }
LAB_0000a996:
            uVar5 = __aeabi_idiv0(0,0,iVar6,uVar7);
            return CONCAT44(param_1,uVar5);
          }
          iVar6 = -0x100;
        }
      }
    }
  }
  while( true ) {
    bVar9 = uVar2 <= param_1 >> 7;
    uVar8 = param_1;
    if (bVar9) {
      uVar8 = param_1 + uVar2 * -0x80;
    }
    bVar13 = uVar2 * 0x80 <= param_1;
    bVar10 = uVar2 <= uVar8 >> 6;
    uVar3 = uVar8;
    if (bVar10) {
      uVar3 = uVar8 + uVar2 * -0x40;
    }
    bVar11 = uVar2 <= uVar3 >> 5;
    uVar4 = uVar3;
    if (bVar11) {
      uVar4 = uVar3 + uVar2 * -0x20;
    }
    bVar12 = uVar2 <= uVar4 >> 4;
    param_1 = uVar4;
    if (bVar12) {
      param_1 = uVar4 + uVar2 * -0x10;
    }
    iVar6 = (((iVar6 * 2 + (uint)(bVar9 && bVar13)) * 2 + (uint)(bVar10 && uVar2 * 0x40 <= uVar8)) *
             2 + (uint)(bVar11 && uVar2 * 0x20 <= uVar3)) * 2 +
            (uint)(bVar12 && uVar2 * 0x10 <= uVar4);
LAB_0000a94e:
    bVar9 = uVar2 <= param_1 >> 3;
    uVar8 = param_1;
    if (bVar9) {
      uVar8 = param_1 + uVar2 * -8;
    }
    uVar3 = iVar6 * 2 + (uint)(bVar9 && uVar2 * 8 <= param_1);
    bVar9 = uVar2 <= uVar8 >> 2;
    param_1 = uVar8;
    if (bVar9) {
      param_1 = uVar8 + uVar2 * -4;
    }
    bVar9 = bVar9 && uVar2 * 4 <= uVar8;
    iVar6 = uVar3 * 2 + (uint)bVar9;
    if (!CARRY4(uVar3,uVar3) && !CARRY4(uVar3 * 2,(uint)bVar9)) break;
    uVar2 = uVar2 >> 6;
  }
  bVar9 = uVar2 <= param_1 >> 1;
  uVar8 = param_1;
  if (bVar9) {
    uVar8 = param_1 + uVar2 * -2;
  }
  uVar3 = uVar8 - uVar2;
  if (uVar2 > uVar8) {
    uVar3 = uVar8;
  }
  iVar6 = (iVar6 * 2 + (uint)(bVar9 && uVar2 * 2 <= param_1)) * 2 + (uint)(uVar2 <= uVar8);
  if ((uVar1 & 1) != 0) {
    iVar6 = -iVar6;
  }
  if ((int)uVar7 < 0) {
    uVar3 = -uVar3;
  }
  return CONCAT44(uVar3,iVar6);
}

