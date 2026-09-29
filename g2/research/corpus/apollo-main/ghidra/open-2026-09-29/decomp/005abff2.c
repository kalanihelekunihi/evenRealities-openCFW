
undefined4 cff_glyph_load(int param_1,int *param_2,undefined4 param_3,uint param_4)

{
  undefined4 uVar1;
  int *piVar2;
  
  if (param_1 == 0) {
    uVar1 = 0x25;
  }
  else {
    if (param_2 == (int *)0x0) {
      param_4 = param_4 | 3;
    }
    piVar2 = param_2;
    if ((int)(param_4 << 0x1f) < 0) {
      piVar2 = (int *)0x0;
    }
    if ((piVar2 == (int *)0x0) || (*param_2 == *(int *)(param_1 + 4))) {
      uVar1 = cff_slot_load(param_1,piVar2);
    }
    else {
      uVar1 = 0x23;
    }
  }
  return uVar1;
}

