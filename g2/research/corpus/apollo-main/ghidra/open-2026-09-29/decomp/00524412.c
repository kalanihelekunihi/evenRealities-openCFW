
undefined8 FT_Get_Advances(int param_1,uint param_2,uint param_3,uint param_4,uint param_5)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  code *pcVar5;
  uint uVar6;
  
  uVar6 = param_3;
  if (param_1 == 0) {
    uVar1 = 0x23;
  }
  else if (param_5 == 0) {
    uVar1 = 6;
  }
  else if (((param_2 < *(uint *)(param_1 + 0x10)) && (param_2 <= param_3 + param_2)) &&
          (param_3 + param_2 <= *(uint *)(param_1 + 0x10))) {
    if (param_3 == 0) {
      uVar1 = 0;
    }
    else {
      pcVar5 = *(code **)(*(int *)(*(int *)(param_1 + 0x60) + 0xc) + 0x54);
      if ((pcVar5 != (code *)0x0) && (((param_4 & 3) != 0 || (((int)param_4 >> 0x10 & 0xfU) == 1))))
      {
        uVar6 = param_5;
        uVar1 = (*pcVar5)(param_1,param_2,param_3,param_4,param_5,param_4);
        if (uVar1 == 0) {
          uVar1 = _ft_face_scale_advances(param_1,param_5,param_3,param_4);
          goto LAB_005244ea;
        }
        if ((uVar1 & 0xff) != 7) goto LAB_005244ea;
      }
      uVar1 = 0;
      if ((int)(param_4 << 2) < 0) {
        uVar1 = 7;
      }
      else {
        if ((int)(param_4 << 0x1f) < 0) {
          iVar3 = 1;
        }
        else {
          iVar3 = 0x400;
        }
        uVar4 = 0;
        while ((uVar4 < param_3 &&
               (uVar1 = FT_Load_Glyph(param_1,uVar4 + param_2,param_4 | 0x100), uVar1 == 0))) {
          if ((int)(param_4 << 0x1b) < 0) {
            iVar2 = *(int *)(*(int *)(param_1 + 0x54) + 0x44);
          }
          else {
            iVar2 = *(int *)(*(int *)(param_1 + 0x54) + 0x40);
          }
          *(int *)(param_5 + uVar4 * 4) = iVar3 * iVar2;
          uVar4 = uVar4 + 1;
        }
      }
    }
  }
  else {
    uVar1 = 0x10;
  }
LAB_005244ea:
  return CONCAT44(uVar6,uVar1);
}

