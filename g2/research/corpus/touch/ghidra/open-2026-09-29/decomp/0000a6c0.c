
undefined8 __aeabi_uidiv(uint param_1,uint param_2)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  undefined4 uVar4;
  int iVar5;
  bool bVar6;
  bool bVar7;
  bool bVar8;
  bool bVar9;
  bool bVar10;
  
  iVar5 = 0;
  if (param_2 <= param_1 >> 1) {
    if (param_2 <= param_1 >> 4) {
      if (param_2 <= param_1 >> 8) {
        if (param_1 >> 0xc < param_2) goto LAB_0000a72c;
        if (param_2 <= param_1 >> 0x10) {
          iVar5 = -0x1000000;
          uVar1 = param_2 << 8;
          if (param_2 << 8 <= param_1 >> 0x10) {
            iVar5 = -0x10000;
            uVar1 = param_2 << 0x10;
            if (param_2 << 0x10 == 0) {
              uVar4 = __aeabi_idiv0(0);
              return CONCAT44(param_1,uVar4);
            }
          }
          param_2 = uVar1;
          if (param_1 >> 0xc < param_2) goto LAB_0000a72c;
        }
        while( true ) {
          bVar6 = param_2 <= param_1 >> 0xf;
          uVar1 = param_1;
          if (bVar6) {
            uVar1 = param_1 + param_2 * -0x8000;
          }
          bVar10 = param_2 * 0x8000 <= param_1;
          bVar7 = param_2 <= uVar1 >> 0xe;
          uVar2 = uVar1;
          if (bVar7) {
            uVar2 = uVar1 + param_2 * -0x4000;
          }
          bVar8 = param_2 <= uVar2 >> 0xd;
          uVar3 = uVar2;
          if (bVar8) {
            uVar3 = uVar2 + param_2 * -0x2000;
          }
          bVar9 = param_2 <= uVar3 >> 0xc;
          param_1 = uVar3;
          if (bVar9) {
            param_1 = uVar3 + param_2 * -0x1000;
          }
          iVar5 = (((iVar5 * 2 + (uint)(bVar6 && bVar10)) * 2 +
                   (uint)(bVar7 && param_2 * 0x4000 <= uVar1)) * 2 +
                  (uint)(bVar8 && param_2 * 0x2000 <= uVar2)) * 2 +
                  (uint)(bVar9 && param_2 * 0x1000 <= uVar3);
LAB_0000a72c:
          bVar6 = param_2 <= param_1 >> 0xb;
          uVar1 = param_1;
          if (bVar6) {
            uVar1 = param_1 + param_2 * -0x800;
          }
          bVar10 = param_2 <= uVar1 >> 10;
          uVar2 = uVar1;
          if (bVar10) {
            uVar2 = uVar1 + param_2 * -0x400;
          }
          bVar7 = param_2 <= uVar2 >> 9;
          uVar3 = uVar2;
          if (bVar7) {
            uVar3 = uVar2 + param_2 * -0x200;
          }
          uVar1 = ((iVar5 * 2 + (uint)(bVar6 && param_2 * 0x800 <= param_1)) * 2 +
                  (uint)(bVar10 && param_2 * 0x400 <= uVar1)) * 2 +
                  (uint)(bVar7 && param_2 * 0x200 <= uVar2);
          bVar6 = param_2 <= uVar3 >> 8;
          param_1 = uVar3;
          if (bVar6) {
            param_1 = uVar3 + param_2 * -0x100;
          }
          bVar6 = bVar6 && param_2 * 0x100 <= uVar3;
          iVar5 = uVar1 * 2 + (uint)bVar6;
          if (!CARRY4(uVar1,uVar1) && !CARRY4(uVar1 * 2,(uint)bVar6)) break;
          param_2 = param_2 >> 8;
        }
      }
      bVar6 = param_2 <= param_1 >> 7;
      uVar1 = param_1;
      if (bVar6) {
        uVar1 = param_1 + param_2 * -0x80;
      }
      bVar10 = param_2 * 0x80 <= param_1;
      bVar7 = param_2 <= uVar1 >> 6;
      uVar2 = uVar1;
      if (bVar7) {
        uVar2 = uVar1 + param_2 * -0x40;
      }
      bVar8 = param_2 <= uVar2 >> 5;
      uVar3 = uVar2;
      if (bVar8) {
        uVar3 = uVar2 + param_2 * -0x20;
      }
      bVar9 = param_2 <= uVar3 >> 4;
      param_1 = uVar3;
      if (bVar9) {
        param_1 = uVar3 + param_2 * -0x10;
      }
      iVar5 = (((iVar5 * 2 + (uint)(bVar6 && bVar10)) * 2 + (uint)(bVar7 && param_2 * 0x40 <= uVar1)
               ) * 2 + (uint)(bVar8 && param_2 * 0x20 <= uVar2)) * 2 +
              (uint)(bVar9 && param_2 * 0x10 <= uVar3);
    }
    bVar6 = param_2 <= param_1 >> 3;
    uVar1 = param_1;
    if (bVar6) {
      uVar1 = param_1 + param_2 * -8;
    }
    bVar10 = param_2 * 8 <= param_1;
    bVar7 = param_2 <= uVar1 >> 2;
    uVar2 = uVar1;
    if (bVar7) {
      uVar2 = uVar1 + param_2 * -4;
    }
    bVar8 = param_2 <= uVar2 >> 1;
    param_1 = uVar2;
    if (bVar8) {
      param_1 = uVar2 + param_2 * -2;
    }
    iVar5 = ((iVar5 * 2 + (uint)(bVar6 && bVar10)) * 2 + (uint)(bVar7 && param_2 * 4 <= uVar1)) * 2
            + (uint)(bVar8 && param_2 * 2 <= uVar2);
  }
  uVar1 = param_1 - param_2;
  if (param_2 > param_1) {
    uVar1 = param_1;
  }
  return CONCAT44(uVar1,iVar5 * 2 + (uint)(param_2 <= param_1));
}

