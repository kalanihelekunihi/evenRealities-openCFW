
/* WARNING: Type propagation algorithm not settling */

uint FUN_00411670(int param_1,uint *param_2,uint *param_3,uint param_4,uint param_5,
                 undefined2 *param_6,code *param_7,undefined4 param_8)

{
  bool bVar1;
  char cVar2;
  byte bVar3;
  short sVar4;
  ushort uVar5;
  undefined2 uVar6;
  ushort uVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  undefined4 uVar12;
  int iVar13;
  uint uVar14;
  uint uVar15;
  uint local_68;
  uint local_64;
  uint local_60;
  int local_5c;
  int local_58;
  int local_54;
  int local_50;
  uint local_4c;
  uint local_48;
  uint local_44 [4];
  uint local_34;
  uint local_30;
  int local_2c;
  uint uStack_28;
  
  local_60 = 0xffffffff;
  if ((*(int *)(param_1 + 0x6c) == 0) ||
     ((*param_3 < *(uint *)(param_1 + 0x6c) && (param_3[1] < *(uint *)(param_1 + 0x6c))))) {
    uStack_28 = param_4;
    FUN_0041560c(local_44,8,0);
    local_58 = 0;
    for (iVar13 = 0; iVar13 < 2; iVar13 = iVar13 + 1) {
      uVar9 = FUN_00410544(param_1,0,param_1,4,param_3[iVar13],0,local_44 + iVar13,4);
      uVar10 = lfs_fromle32(local_44[iVar13]);
      local_44[iVar13] = uVar10;
      if ((uVar9 != 0) && (uVar9 != 0xffffffac)) {
        return uVar9;
      }
      if ((uVar9 != 0xffffffac) &&
         (iVar8 = lfs_scmp(local_44[iVar13],local_44[(iVar13 + 1) % 2]), 0 < iVar8)) {
        local_58 = iVar13;
      }
    }
    *param_2 = param_3[local_58 % 2];
    param_2[1] = param_3[(local_58 + 1) % 2];
    param_2[2] = local_44[local_58 % 2];
    param_2[3] = 0;
    local_44[2] = param_4;
    for (local_50 = 0; uVar9 = local_60, local_50 < 2; local_50 = local_50 + 1) {
      iVar13 = 0;
      uVar10 = 0xffffffff;
      uVar7 = 0;
      local_4c = *DAT_00412204;
      local_48 = DAT_00412204[1];
      bVar3 = 0;
      local_64 = local_64 & 0xffffff00;
      bVar1 = false;
      uVar11 = lfs_tole32(param_2[2]);
      param_2[2] = uVar11;
      local_5c = FUN_004157c0(0xffffffff,param_2 + 2,4);
      uVar11 = lfs_fromle32(param_2[2]);
      param_2[2] = uVar11;
      while( true ) {
        iVar8 = FUN_00410bc6(uVar10);
        iVar13 = iVar8 + iVar13;
        uVar11 = FUN_00410544(param_1,0,param_1,*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x1c),
                              *param_2,iVar13,&local_68,4);
        if (uVar11 != 0) break;
        local_5c = FUN_004157c0(local_5c,&local_68,4);
        local_68 = lfs_frombe32(local_68);
        local_68 = local_68 ^ uVar10;
        iVar8 = lfs_tag_isvalid(local_68);
        if (iVar8 == 0) {
          iVar13 = FUN_00410b98(uVar10);
          if (iVar13 == 0x500) {
            local_64 = CONCAT31(local_64._1_3_,1);
          }
          else {
            local_64 = (uint)local_64._1_3_ << 8;
          }
          goto LAB_00411778;
        }
        iVar8 = FUN_00410bc6(local_68);
        uVar10 = local_68;
        if (*(uint *)(*(int *)(param_1 + 0x68) + 0x1c) < (uint)(iVar8 + iVar13)) goto LAB_00411778;
        iVar8 = FUN_00410b98(local_68);
        if (iVar8 == 0x500) {
          uVar11 = FUN_00410544(param_1,0,param_1,*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x1c),
                                *param_2,iVar13 + 4,&local_54,4);
          if (uVar11 != 0) break;
          local_54 = lfs_fromle32(local_54);
          if (local_5c != local_54) goto LAB_00411778;
          iVar8 = lfs_tag_chunk(local_68);
          uVar10 = uVar10 ^ iVar8 << 0x1f;
          uVar12 = FUN_004157c0(*(undefined4 *)(param_1 + 0x2c),&local_5c,4);
          *(undefined4 *)(param_1 + 0x2c) = uVar12;
          local_60 = uVar9;
          iVar8 = FUN_00410bc6(local_68);
          param_2[3] = iVar8 + iVar13;
          param_2[4] = uVar10;
          *(ushort *)(param_2 + 5) = uVar7;
          param_2[6] = local_4c;
          param_2[7] = local_48;
          *(byte *)((int)param_2 + 0x17) = bVar3;
          local_5c = -1;
        }
        else {
          iVar8 = FUN_00410bc6(local_68);
          uVar11 = FUN_00410790(param_1,0,param_1,*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x1c),
                                *param_2,iVar13 + 4,iVar8 + -4,&local_5c);
          if (uVar11 != 0) break;
          iVar8 = lfs_tag_type1(local_68);
          uVar14 = uVar9;
          if (iVar8 == 0) {
            uVar9 = lfs_tag_id(local_68);
            if (uVar7 <= uVar9) {
              sVar4 = lfs_tag_id(local_68);
              uVar7 = sVar4 + 1;
            }
          }
          else {
            iVar8 = lfs_tag_type1(local_68);
            if (iVar8 == 0x400) {
              cVar2 = FUN_00410bae(local_68);
              uVar7 = (short)cVar2 + uVar7;
              if (local_68 == (DAT_00411c40 & uVar9 | DAT_00411e40)) {
                uVar14 = uVar9 | 0x80000000;
              }
              else if (uVar9 != 0xffffffff) {
                uVar5 = lfs_tag_id(uVar9);
                uVar15 = (uint)uVar5;
                uVar11 = lfs_tag_id(local_68);
                if (uVar11 <= (uVar15 & 0xffff)) {
                  iVar8 = FUN_00410bae(local_68);
                  uVar14 = uVar9 + iVar8 * 0x400;
                }
              }
            }
            else {
              iVar8 = lfs_tag_type1(local_68);
              if (iVar8 == 0x600) {
                bVar3 = lfs_tag_chunk(local_68);
                bVar3 = bVar3 & 1;
                uVar11 = FUN_00410544(param_1,0,param_1,
                                      *(undefined4 *)(*(int *)(param_1 + 0x68) + 0x1c),*param_2,
                                      iVar13 + 4,&local_4c,8);
                if (uVar11 != 0) break;
                FUN_00410b46(&local_4c);
              }
              else {
                iVar8 = lfs_tag_type3(local_68);
                if (iVar8 == 0x5ff) {
                  iVar8 = FUN_00410544(param_1,0,param_1,
                                       *(undefined4 *)(*(int *)(param_1 + 0x68) + 0x1c),*param_2,
                                       iVar13 + 4,local_44 + 3,8);
                  if ((iVar8 != 0) && (iVar8 == -0x54)) goto LAB_00411778;
                  FUN_00410cc6(local_44 + 3);
                  bVar1 = true;
                }
              }
            }
          }
          uVar9 = uVar14;
          if ((local_44[2] & local_68) == (local_44[2] & param_5)) {
            local_30 = *param_2;
            local_2c = iVar13 + 4;
            uVar11 = (*param_7)(param_8,local_68,&local_30);
            if ((int)uVar11 < 0) break;
            uVar9 = local_68;
            if (uVar11 != 0) {
              if ((local_68 & DAT_00411e38) == (DAT_00411e38 & uVar14)) {
                uVar9 = 0xffffffff;
              }
              else {
                uVar9 = uVar14;
                if (uVar11 == 2) {
                  uVar5 = lfs_tag_id(uVar14);
                  uVar15 = (uint)uVar5;
                  uVar11 = lfs_tag_id(local_68);
                  if (uVar11 <= (uVar15 & 0xffff)) {
                    uVar9 = local_68 | 0x80000000;
                  }
                }
              }
            }
          }
        }
      }
      if (uVar11 != 0xffffffac) {
        return uVar11;
      }
LAB_00411778:
      if (param_2[3] != 0) {
        *(undefined1 *)((int)param_2 + 0x16) = 0;
        if ((((char)local_64 != '\0') &&
            (uVar9 = *(uint *)(*(int *)(param_1 + 0x68) + 0x18),
            param_2[3] == uVar9 * (param_2[3] / uVar9))) && (bVar1)) {
          local_64 = 0xffffffff;
          uVar9 = FUN_00410790(param_1,0,param_1,*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x1c),
                               *param_2,param_2[3],local_44[3],&local_64);
          if ((uVar9 != 0) && (uVar9 != 0xffffffac)) {
            return uVar9;
          }
          *(bool *)((int)param_2 + 0x16) = local_64 == local_34;
        }
        iVar13 = FUN_00410c64(param_1 + 0x3c,param_2);
        if (iVar13 != 0) {
          uVar9 = lfs_tag_id(*(undefined4 *)(param_1 + 0x3c));
          uVar10 = lfs_tag_id(local_60);
          if ((uVar9 & 0xffff) == uVar10) {
            local_60 = local_60 | 0x80000000;
          }
          else if (local_60 != 0xffffffff) {
            uVar9 = lfs_tag_id(*(undefined4 *)(param_1 + 0x3c));
            uVar10 = lfs_tag_id(local_60);
            if ((uVar9 & 0xffff) < uVar10) {
              local_60 = local_60 - 0x400;
            }
          }
        }
        if (param_6 != (undefined2 *)0x0) {
          uVar6 = lfs_tag_id(local_60);
          uVar6 = lfs_min(uVar6,(short)param_2[5]);
          *param_6 = uVar6;
        }
        iVar13 = lfs_tag_isvalid(local_60);
        if (iVar13 == 0) {
          uVar7 = lfs_tag_id(local_60);
          if ((ushort)param_2[5] <= uVar7) {
            return 0;
          }
          return 0xfffffffe;
        }
        return local_60;
      }
      FUN_00410ace(param_2);
      param_2[2] = local_44[(local_58 + 1) % 2];
    }
    FUN_00415fae(DAT_0041276c,DAT_00411e48,0x569,*param_2,param_2[1],&DAT_00411c48);
  }
  return 0xffffffac;
}

