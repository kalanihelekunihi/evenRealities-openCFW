
undefined4 tt_glyph_load(int param_1,int param_2,uint param_3,uint param_4)

{
  undefined4 uVar1;
  uint uVar2;
  int iVar3;
  
  iVar3 = *(int *)(param_1 + 4);
  if (param_1 == 0) {
    uVar1 = 0x25;
  }
  else if (param_2 == 0) {
    uVar1 = 0x24;
  }
  else if (iVar3 == 0) {
    uVar1 = 0x23;
  }
  else if ((param_3 < *(uint *)(iVar3 + 0x10)) || (*(int *)(*(int *)(iVar3 + 0x80) + 0x34) != 0)) {
    if ((int)(param_4 << 0x1e) < 0) {
      if (*(int *)(iVar3 + 8) << 0x12 < 0) {
        param_4 = param_4 & 0xfffffffd;
      }
      if ((int)(param_4 << 0x10) < 0) {
        param_4 = param_4 | 2;
      }
    }
    uVar2 = param_4;
    if (((param_4 & 0x401) != 0) && (uVar2 = param_4 | 9, -1 < *(int *)(iVar3 + 8) << 0x12)) {
      uVar2 = param_4 | 0xb;
    }
    if ((int)(uVar2 << 0x1e) < 0) {
      iVar3 = 0xc;
    }
    else {
      iVar3 = 0x30;
    }
    *(int *)(param_2 + 0x2c) = param_2 + iVar3;
    uVar1 = TT_Load_Glyph();
  }
  else {
    uVar1 = 6;
  }
  return uVar1;
}

