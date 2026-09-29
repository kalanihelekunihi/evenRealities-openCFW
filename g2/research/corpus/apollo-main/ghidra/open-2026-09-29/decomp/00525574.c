
undefined8 FT_Load_Glyph(int param_1,uint param_2,uint param_3,undefined4 param_4)

{
  bool bVar1;
  bool bVar2;
  int iVar3;
  int *piVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  undefined4 *puVar9;
  undefined4 uVar10;
  uint uVar11;
  
  bVar2 = false;
  uVar11 = param_2;
  if (((param_1 == 0) || (*(int *)(param_1 + 0x58) == 0)) || (*(int *)(param_1 + 0x54) == 0)) {
    iVar3 = 0x23;
  }
  else {
    iVar7 = *(int *)(param_1 + 0x54);
    ft_glyphslot_clear(iVar7);
    puVar9 = *(undefined4 **)(param_1 + 0x60);
    piVar4 = *(int **)(puVar9[1] + 0xa0);
    if ((int)(param_3 << 0x15) < 0) {
      param_3 = param_3 | 0x801;
    }
    if ((int)(param_3 << 0x1f) < 0) {
      param_3 = param_3 & 0xfffffffb | 10;
    }
    if ((int)(param_3 << 9) < 0) {
      param_3 = param_3 & 0xfffffffb;
    }
    if ((((piVar4 != (int *)0x0) && ((param_3 & 0x8002) == 0)) &&
        (((*(uint *)*puVar9 & 0x300) == 0x100 && (-1 < *(int *)(param_1 + 8) << 0x12)))) &&
       ((((int)(param_3 << 0x14) < 0 ||
         ((*(int *)(*(int *)(param_1 + 0x80) + 8) == 0 && (**(int **)(param_1 + 0x80) != 0)))) ||
        ((**(int **)(param_1 + 0x80) == 0 && (*(int *)(*(int *)(param_1 + 0x80) + 8) != 0)))))) {
      if (((int)(param_3 << 0x1a) < 0) || (-1 < *(int *)*puVar9 << 0x15)) {
        bVar2 = true;
      }
      else {
        uVar10 = FT_Get_Font_Format(param_1);
        iVar3 = FUN_0044b63a(uVar10,DAT_005261a8);
        if ((iVar3 == 0) || (puVar9[7] != 1)) {
          bVar1 = false;
        }
        else {
          bVar1 = true;
        }
        if ((((((int)param_3 >> 0x10 & 0xfU) == 1) && (-1 < *(int *)*puVar9 << 0x14)) && (!bVar1))
           || ((((int)((uint)*(byte *)(param_1 + 8) << 0x1c) < 0 && (*(int *)(param_1 + 0x2d4) != 0)
                ) && ((*(short *)(param_1 + 0x11e) == 0 &&
                      ((*(int *)(param_1 + 0x288) == 0 && (*(int *)(param_1 + 0x290) == 0)))))))) {
          bVar2 = true;
        }
      }
    }
    if (bVar2) {
      if ((((-1 < (int)((uint)*(byte *)(param_1 + 8) << 0x1e)) || ((int)(param_3 << 0x1c) < 0)) ||
          (iVar3 = (**(code **)(puVar9[3] + 0x48))
                             (iVar7,*(undefined4 *)(param_1 + 0x58),param_2,param_3 | 0x4000),
          iVar3 != 0)) || (iVar3 = 0, *(int *)(iVar7 + 0x48) != s_stibltuopmoccff_0052628c._0_4_)) {
        iVar8 = *(int *)(param_1 + 0x80);
        uVar10 = *(undefined4 *)(iVar8 + 0x18);
        *(undefined4 *)(iVar8 + 0x18) = 0;
        uVar11 = param_3;
        iVar3 = (**(code **)(*(int *)(*piVar4 + 0x14) + 0xc))
                          (piVar4,iVar7,*(undefined4 *)(param_1 + 0x58),param_2);
        *(undefined4 *)(iVar8 + 0x18) = uVar10;
      }
    }
    else {
      iVar3 = (**(code **)(puVar9[3] + 0x48))
                        (iVar7,*(undefined4 *)(param_1 + 0x58),param_2,param_3,uVar11,piVar4,param_4
                        );
      if (iVar3 != 0) goto LAB_0052582e;
      if (*(int *)(iVar7 + 0x48) == s_stibltuopmoccff_0052628c._4_4_) {
        iVar3 = FT_Outline_Check(iVar7 + 0x6c);
        if (iVar3 != 0) goto LAB_0052582e;
        if (-1 < (int)(param_3 << 0x1e)) {
          ft_glyphslot_grid_fit_metrics(iVar7,param_3 & 0x10);
        }
      }
    }
    if ((int)(param_3 << 0x1b) < 0) {
      *(undefined4 *)(iVar7 + 0x40) = 0;
      *(undefined4 *)(iVar7 + 0x44) = *(undefined4 *)(iVar7 + 0x34);
    }
    else {
      *(undefined4 *)(iVar7 + 0x40) = *(undefined4 *)(iVar7 + 0x28);
      *(undefined4 *)(iVar7 + 0x44) = 0;
    }
    if ((-1 < (int)(param_3 << 0x12)) && ((int)((uint)*(byte *)(param_1 + 8) << 0x1f) < 0)) {
      iVar8 = *(int *)(param_1 + 0x58);
      uVar10 = FT_MulDiv(*(undefined4 *)(iVar7 + 0x38),*(undefined4 *)(iVar8 + 0x10),0x40);
      *(undefined4 *)(iVar7 + 0x38) = uVar10;
      uVar10 = FT_MulDiv(*(undefined4 *)(iVar7 + 0x3c),*(undefined4 *)(iVar8 + 0x14),0x40);
      *(undefined4 *)(iVar7 + 0x3c) = uVar10;
    }
    if ((-1 < (int)(param_3 << 0x14)) &&
       (iVar8 = *(int *)(param_1 + 0x80), *(int *)(iVar8 + 0x18) != 0)) {
      iVar5 = ft_lookup_glyph_renderer(iVar7);
      if (iVar5 == 0) {
        if (*(int *)(iVar7 + 0x48) == s_stibltuopmoccff_0052628c._4_4_) {
          if ((int)((uint)*(byte *)(iVar8 + 0x18) << 0x1f) < 0) {
            FT_Outline_Transform(iVar7 + 0x6c,iVar8);
          }
          if ((int)((uint)*(byte *)(iVar8 + 0x18) << 0x1e) < 0) {
            FT_Outline_Translate
                      (iVar7 + 0x6c,*(undefined4 *)(iVar8 + 0x10),*(undefined4 *)(iVar8 + 0x14));
          }
        }
      }
      else {
        iVar3 = (**(code **)(*(int *)(iVar5 + 0xc) + 0x2c))(iVar5,iVar7,iVar8,iVar8 + 0x10);
      }
      FT_Vector_Transform(iVar7 + 0x40,iVar8);
    }
    if ((((iVar3 == 0) && (-1 < (int)(param_3 << 0x1f))) &&
        (*(int *)(iVar7 + 0x48) != s_stibltuopmoccff_0052628c._0_4_)) &&
       (*(int *)(iVar7 + 0x48) != s_stibltuopmoccff_0052628c._8_4_)) {
      uVar6 = (int)param_3 >> 0x10 & 0xf;
      if ((uVar6 == 0) && ((int)(param_3 << 0x13) < 0)) {
        uVar6 = 2;
      }
      if ((int)(param_3 << 0x1d) < 0) {
        iVar3 = FT_Render_Glyph(iVar7,uVar6);
      }
      else {
        ft_glyphslot_preset_bitmap(iVar7,uVar6,0);
      }
    }
  }
LAB_0052582e:
  return CONCAT44(uVar11,iVar3);
}

