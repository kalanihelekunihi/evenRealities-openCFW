
undefined8 _ft_face_scale_advances(int param_1,int param_2,uint param_3,int param_4)

{
  undefined4 uVar1;
  undefined4 uVar2;
  uint uVar3;
  
  if (param_4 << 0x1f < 0) {
    uVar1 = 0;
  }
  else if (*(int *)(param_1 + 0x58) == 0) {
    uVar1 = 0x24;
  }
  else {
    if (param_4 << 0x1b < 0) {
      uVar1 = *(undefined4 *)(*(int *)(param_1 + 0x58) + 0x14);
    }
    else {
      uVar1 = *(undefined4 *)(*(int *)(param_1 + 0x58) + 0x10);
    }
    for (uVar3 = 0; uVar3 < param_3; uVar3 = uVar3 + 1) {
      uVar2 = FT_MulDiv(*(undefined4 *)(param_2 + uVar3 * 4),uVar1,0x40);
      *(undefined4 *)(param_2 + uVar3 * 4) = uVar2;
    }
    uVar1 = 0;
  }
  return CONCAT44(param_4,uVar1);
}

