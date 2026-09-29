
int af_loader_load_glyph(int param_1,int param_2,int param_3,undefined4 param_4,uint param_5)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int *local_70;
  int *local_6c;
  int local_68;
  uint local_64;
  uint local_60;
  uint local_5c;
  uint local_58;
  int local_54;
  undefined4 local_50;
  undefined4 local_4c;
  undefined4 local_48;
  undefined4 local_44;
  byte local_40;
  undefined4 local_3c;
  undefined1 auStack_38 [16];
  undefined4 local_28;
  
  local_68 = *(int *)(param_3 + 0x58);
  iVar8 = *(int *)(local_68 + 0x28);
  iVar5 = *(int *)(param_3 + 0x54);
  local_6c = *(int **)(iVar5 + 0x9c);
  iVar6 = *local_6c;
  iVar7 = *(int *)(param_1 + 8);
  local_64 = 0x40;
  if (local_68 == 0) {
    iVar8 = 0x24;
  }
  else {
    local_28 = param_4;
    FUN_0043c0e4(&local_54,0x1c,0);
    local_40 = (byte)(param_5 >> 0x10);
    if ((*(int *)(iVar8 + 0xc) == 0) ||
       ((uint)*(byte *)(iVar8 + 4) != ((int)param_5 >> 0x10 & 0xfU))) {
      *(byte *)(iVar8 + 4) = local_40 & 0xf;
      FUN_00439c04(iVar8 + 8,local_68 + 0xc,0x1c);
    }
    local_50 = *(undefined4 *)(iVar8 + 0xc);
    local_48 = 0;
    local_4c = *(undefined4 *)(iVar8 + 0x10);
    local_44 = 0;
    local_40 = local_40 & 0xf;
    local_3c = 0;
    local_68 = param_2;
    local_54 = param_3;
    iVar8 = af_loader_reset(param_1,param_2,param_3);
    if ((iVar8 == 0) &&
       (iVar8 = af_face_globals_get_metrics
                          (*(undefined4 *)(param_1 + 4),local_28,local_64,&local_70), iVar8 == 0)) {
      iVar9 = *(int *)(DAT_005abc34 + (uint)*(byte *)(*local_70 + 1) * 4);
      *(int **)(param_1 + 0xc) = local_70;
      if (*(int *)(iVar9 + 0xc) == 0) {
        FUN_00439c04(local_70 + 1,&local_54,0x1c);
      }
      else {
        (**(code **)(iVar9 + 0xc))(local_70,&local_54);
      }
      if (((*(int *)(iVar9 + 0x18) == 0) ||
          (iVar8 = (**(code **)(iVar9 + 0x18))(iVar7,local_70), iVar8 == 0)) &&
         (iVar8 = FT_Load_Glyph(param_3,local_28,param_5 & 0xfffffffb | 0x2801), iVar8 == 0)) {
        if ((local_40 == 1) &&
           ((*(char *)(*(int *)(param_3 + 0x80) + 0x38) == '\0' ||
            ((*(char *)(*(int *)(param_3 + 0x80) + 0x38) < '\0' &&
             (*(char *)(local_68 + 0x15) == '\0')))))) {
          af_loader_embolden_glyph_in_slot(param_1,param_3,local_70);
        }
        *(char *)(param_1 + 0x10) = (char)local_6c[2];
        if (*(char *)(param_1 + 0x10) != '\0') {
          FUN_00439c04(param_1 + 0x14,local_6c + 3,0x10);
          iVar3 = local_6c[8];
          *(int *)(param_1 + 0x24) = local_6c[7];
          *(int *)(param_1 + 0x28) = iVar3;
          FUN_00439c04(auStack_38,param_1 + 0x14,0x10);
          iVar3 = FT_Matrix_Invert(auStack_38);
          if (iVar3 == 0) {
            FT_Vector_Transform(param_1 + 0x24,auStack_38);
          }
        }
        iVar3 = DAT_005abc38;
        if (*(int *)(iVar5 + 0x48) == DAT_005abc38) {
          if (*(char *)(param_1 + 0x10) != '\0') {
            FT_Outline_Translate
                      (iVar5 + 0x6c,*(undefined4 *)(param_1 + 0x24),*(undefined4 *)(param_1 + 0x28))
            ;
          }
          *(undefined4 *)(param_1 + 0x2c) = *(undefined4 *)(iVar7 + 8);
          *(undefined4 *)(param_1 + 0x30) = *(undefined4 *)(iVar7 + 0x10);
          iVar1 = FT_MulFix(*(undefined4 *)(iVar5 + 0x28),*(undefined4 *)(iVar7 + 4));
          *(int *)(param_1 + 0x34) = *(int *)(iVar7 + 8) + iVar1;
          *(undefined4 *)(param_1 + 0x38) = *(undefined4 *)(iVar7 + 0x10);
          if (*(short *)(iVar5 + 0x6e) != 0) {
            if (*(int *)(iVar9 + 0x1c) != 0) {
              (**(code **)(iVar9 + 0x1c))(local_28,iVar7,iVar6 + 0x14,local_70);
            }
            if (local_40 == 1) {
              iVar7 = *(int *)(param_1 + 0x2c);
              iVar9 = *(int *)(param_1 + 0x34);
              *(uint *)(param_1 + 0x2c) = iVar7 + 0x20U & 0xffffffc0;
              *(uint *)(param_1 + 0x34) = iVar9 + 0x20U & 0xffffffc0;
              *(int *)(iVar5 + 0x90) = *(int *)(param_1 + 0x2c) - iVar7;
              *(int *)(iVar5 + 0x94) = *(int *)(param_1 + 0x34) - iVar9;
            }
            else {
              iVar1 = *(int *)(iVar7 + 0x40);
              iVar9 = iVar1 + *(int *)(iVar7 + 0x38) * 0x2c;
              if ((*(int *)(iVar7 + 0x38) < 2) ||
                 ((int)((uint)*(byte *)(iVar7 + 0xab4) << 0x1d) < 0)) {
                iVar9 = *(int *)(param_1 + 0x2c);
                iVar1 = *(int *)(param_1 + 0x34);
                *(uint *)(param_1 + 0x2c) = *(int *)(iVar7 + 0xac0) + iVar9 + 0x20U & 0xffffffc0;
                *(uint *)(param_1 + 0x34) = *(int *)(iVar7 + 0xac4) + iVar1 + 0x20U & 0xffffffc0;
                *(int *)(iVar5 + 0x90) = *(int *)(param_1 + 0x2c) - iVar9;
                *(int *)(iVar5 + 0x94) = *(int *)(param_1 + 0x34) - iVar1;
              }
              else {
                iVar4 = *(int *)(param_1 + 0x34) - *(int *)(iVar9 + -0x28);
                iVar7 = *(int *)(iVar1 + 4);
                iVar11 = *(int *)(iVar1 + 8);
                iVar1 = iVar11 - iVar7;
                iVar10 = iVar4 + *(int *)(iVar9 + -0x24);
                if (iVar7 < 0x18) {
                  iVar1 = iVar1 + -8;
                }
                if (iVar4 < 0x18) {
                  iVar10 = iVar10 + 8;
                }
                *(uint *)(param_1 + 0x2c) = iVar1 + 0x20U & 0xffffffc0;
                *(uint *)(param_1 + 0x34) = iVar10 + 0x20U & 0xffffffc0;
                if ((iVar11 <= *(int *)(param_1 + 0x2c)) && (0 < iVar7)) {
                  *(int *)(param_1 + 0x2c) = *(int *)(param_1 + 0x2c) + -0x40;
                }
                if ((*(int *)(param_1 + 0x34) <= *(int *)(iVar9 + -0x24)) && (0 < iVar4)) {
                  *(int *)(param_1 + 0x34) = *(int *)(param_1 + 0x34) + 0x40;
                }
                *(int *)(iVar5 + 0x90) = *(int *)(param_1 + 0x2c) - iVar1;
                *(int *)(iVar5 + 0x94) = *(int *)(param_1 + 0x34) - iVar10;
              }
            }
          }
        }
        else {
          iVar8 = 7;
        }
        local_6c = (int *)(*(int *)(iVar5 + 0x2c) - *(int *)(iVar5 + 0x20));
        local_68 = *(int *)(iVar5 + 0x30) - *(int *)(iVar5 + 0x24);
        local_6c = (int *)FT_MulFix(local_6c,local_70[2]);
        local_68 = FT_MulFix(local_68,local_70[3]);
        if (*(char *)(param_1 + 0x10) != '\0') {
          FT_Outline_Transform(iVar6 + 0x14,param_1 + 0x14);
          FT_Vector_Transform(&local_6c,param_1 + 0x14);
        }
        if (*(int *)(param_1 + 0x2c) != 0) {
          FT_Outline_Translate(iVar6 + 0x14,-*(int *)(param_1 + 0x2c),0);
        }
        FT_Outline_Get_CBox(iVar6 + 0x14,&local_64);
        local_64 = local_64 & 0xffffffc0;
        local_60 = local_60 & 0xffffffc0;
        local_5c = local_5c + 0x3f & 0xffffffc0;
        local_58 = local_58 + 0x3f & 0xffffffc0;
        *(uint *)(iVar5 + 0x18) = local_5c - local_64;
        *(uint *)(iVar5 + 0x1c) = local_58 - local_60;
        *(uint *)(iVar5 + 0x20) = local_64;
        *(uint *)(iVar5 + 0x24) = local_58;
        *(uint *)(iVar5 + 0x2c) = (int)local_6c + local_64 & 0xffffffc0;
        *(uint *)(iVar5 + 0x30) = local_68 + local_58 & 0xffffffc0;
        if ((local_40 == 1) ||
           ((-1 < (int)((uint)*(byte *)(*(int *)(iVar5 + 4) + 8) << 0x1d) &&
            ((iVar6 = af_face_globals_is_digit(*(undefined4 *)(param_1 + 4),local_28), iVar6 == 0 ||
             ((char)local_70[8] == '\0')))))) {
          if (*(int *)(iVar5 + 0x28) != 0) {
            *(int *)(iVar5 + 0x28) = *(int *)(param_1 + 0x34) - *(int *)(param_1 + 0x2c);
          }
        }
        else {
          uVar2 = FT_MulFix(*(undefined4 *)(iVar5 + 0x28),local_70[2]);
          *(undefined4 *)(iVar5 + 0x28) = uVar2;
          *(undefined4 *)(iVar5 + 0x90) = 0;
          *(undefined4 *)(iVar5 + 0x94) = 0;
        }
        uVar2 = FT_MulFix(*(undefined4 *)(iVar5 + 0x34),local_70[3]);
        *(undefined4 *)(iVar5 + 0x34) = uVar2;
        *(uint *)(iVar5 + 0x28) = *(int *)(iVar5 + 0x28) + 0x20U & 0xffffffc0;
        *(uint *)(iVar5 + 0x34) = *(int *)(iVar5 + 0x34) + 0x20U & 0xffffffc0;
        *(int *)(iVar5 + 0x48) = iVar3;
      }
    }
  }
  return iVar8;
}

