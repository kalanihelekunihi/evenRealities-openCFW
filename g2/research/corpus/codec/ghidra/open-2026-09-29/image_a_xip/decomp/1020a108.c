
/* WARNING: Removing unreachable block (ram,0x1020a292) */

void gx8002_muldf3_fixed(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4
                        )

{
  bool bVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  undefined4 *puVar6;
  uint uVar7;
  uint uVar8;
  int iVar9;
  int iVar10;
  uint uVar11;
  undefined4 uStack_70;
  undefined4 uStack_6c;
  undefined4 uStack_68;
  undefined4 uStack_64;
  uint uStack_60;
  uint uStack_5c;
  int iStack_58;
  undefined4 uStack_54;
  undefined4 uStack_50;
  uint uStack_4c;
  uint uStack_48;
  int iStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  uint uStack_34;
  int iStack_30;
  uint uStack_2c;
  uint uStack_28;
  
  uStack_70 = param_1;
  uStack_6c = param_2;
  uStack_68 = param_3;
  uStack_64 = param_4;
  gx8002_unpack_double(&uStack_70,&uStack_60);
  gx8002_unpack_double(&uStack_68,&uStack_4c);
  if (1 < uStack_60) {
    if (uStack_4c < 2) {
LAB_1020a256:
      uStack_48 = (uint)(uStack_5c != uStack_48);
      gx8002_pack_double(&uStack_4c);
      return;
    }
    puVar6 = (undefined4 *)PTR_gx8002_fpadd_parts_nan_1020a304;
    if (uStack_60 == 4) {
      if (uStack_4c != 2) goto LAB_1020a270;
    }
    else if (uStack_4c == 4) {
      if (uStack_60 != 2) goto LAB_1020a256;
    }
    else {
      if (uStack_60 == 2) goto LAB_1020a270;
      if (uStack_4c == 2) goto LAB_1020a256;
      uVar7 = 0;
      uVar2 = gx8002_muldi3(uStack_40,0,uStack_54);
      uVar8 = 0;
      uVar3 = gx8002_muldi3(uStack_3c,0,uStack_54);
      iVar9 = 0;
      uVar4 = gx8002_muldi3(uStack_50,0,uStack_3c);
      iVar10 = 0;
      uVar5 = gx8002_muldi3(uStack_50,0,uStack_40);
      uVar11 = iVar10 + uVar8 + (uint)CARRY4(uVar5,uVar3);
      if ((uVar11 < uVar8) || ((uVar8 == uVar11 && (uVar5 + uVar3 < uVar3)))) {
        iVar10 = 1;
      }
      else {
        iVar10 = 0;
      }
      uVar3 = uVar5 + uVar3 + uVar7;
      uStack_2c = (uint)(uVar3 < uVar7) + uVar4 + uVar11;
      uStack_28 = iVar10 + iVar9 + (uint)CARRY4(uVar4,uVar11) +
                  (uint)CARRY4((uint)(uVar3 < uVar7),uVar4 + uVar11);
      iStack_58 = iStack_58 + iStack_44;
      iStack_30 = iStack_58 + 4;
      uStack_34 = (uint)(uStack_5c != uStack_48);
      if (uStack_28 < 0x20000000) {
        if (uStack_28 < 0x10000000) {
          iVar9 = iStack_58 + 3;
          do {
            iStack_30 = iVar9;
            bVar1 = CARRY4(uStack_2c,uStack_2c);
            uStack_2c = uStack_2c * 2;
            uStack_28 = uStack_28 * 2 + (uint)bVar1;
            if ((int)uVar3 < 0) {
              uStack_2c = uStack_2c | 1;
            }
            bVar1 = CARRY4(uVar2,uVar2);
            uVar2 = uVar2 * 2;
            uVar3 = uVar3 * 2 + (uint)bVar1;
            iVar9 = iStack_30 + -1;
          } while (uStack_28 < 0x10000000);
        }
      }
      else {
        iVar9 = iStack_58 + 5;
        uVar4 = uStack_28;
        do {
          iStack_30 = iVar9;
          if ((uStack_2c & 1) != 0) {
            uVar2 = uVar2 >> 1 | uVar3 << 0x1f;
            uVar3 = uVar3 >> 1;
          }
          uStack_28 = uVar4 >> 1;
          uStack_2c = uVar4 << 0x1f | uStack_2c >> 1;
          iVar9 = iStack_30 + 1;
          uVar4 = uStack_28;
        } while (0x1fffffff < uStack_28);
      }
      if ((((uStack_2c & 0xff) == 0x80) && ((uStack_2c & 0x100) == 0)) && (uVar2 != 0 || uVar3 != 0)
         ) {
        uStack_28 = uStack_28 + (0xffffff7f < uStack_2c);
        uStack_2c = uStack_2c + 0x80 & 0xffffff00;
      }
      uStack_38 = 3;
      puVar6 = &uStack_38;
    }
    gx8002_pack_double(puVar6);
    return;
  }
LAB_1020a270:
  uStack_5c = (uint)(uStack_5c != uStack_48);
  gx8002_pack_double(&uStack_60);
  return;
}

