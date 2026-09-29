
undefined8 FT_Get_Advance(int param_1,uint param_2,uint param_3,int param_4)

{
  uint uVar1;
  code *pcVar2;
  
  if (param_1 == 0) {
    uVar1 = 0x23;
  }
  else if (param_4 == 0) {
    uVar1 = 6;
  }
  else if (param_2 < *(uint *)(param_1 + 0x10)) {
    pcVar2 = *(code **)(*(int *)(*(int *)(param_1 + 0x60) + 0xc) + 0x54);
    if ((pcVar2 != (code *)0x0) && (((param_3 & 3) != 0 || (((int)param_3 >> 0x10 & 0xfU) == 1)))) {
      uVar1 = (*pcVar2)(param_1,param_2,1,param_3);
      if (uVar1 == 0) {
        uVar1 = _ft_face_scale_advances(param_1,param_4,1,param_3);
        goto LAB_00524410;
      }
      if ((uVar1 & 0xff) != 7) goto LAB_00524410;
    }
    uVar1 = FT_Get_Advances(param_1,param_2,1,param_3);
  }
  else {
    uVar1 = 0x10;
  }
LAB_00524410:
  return CONCAT44(param_4,uVar1);
}

