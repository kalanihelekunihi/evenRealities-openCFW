
short attsIsHashableAttr(int *param_1)

{
  short sVar1;
  int iVar2;
  
  sVar1 = 2;
  if (*DAT_0053546c != '\0') {
    *DAT_0053546c = '\0';
    return 0;
  }
  iVar2 = (uint)*(byte *)(*param_1 + 1) * 0x100 + (uint)*(byte *)*param_1;
  if (2 < iVar2 - 0x2800U) {
    if (iVar2 == 0x2803) {
      *DAT_0053546c = '\x01';
    }
    else if (iVar2 != 0x2900) {
      if ((2 < iVar2 - 0x2901U) && (iVar2 - 0x2901U != 4)) {
        return 0;
      }
      goto LAB_00534ef8;
    }
  }
  sVar1 = *(short *)param_1[2] + 2;
LAB_00534ef8:
  if ((int)((uint)*(byte *)((int)param_1 + 0xe) << 0x1f) < 0) {
    sVar1 = sVar1 + 0x10;
  }
  else {
    sVar1 = sVar1 + 2;
  }
  return sVar1;
}

