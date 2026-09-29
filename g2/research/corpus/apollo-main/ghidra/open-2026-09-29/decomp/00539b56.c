
undefined8 FUN_00539b56(uint *param_1)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r7;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_00539dac)) {
    uVar1 = 2;
  }
  else if ((int)(*DAT_00539db4 << 2) < 0) {
    if ((*DAT_00539db4 >> 9 & 1) == 1) {
      iVar2 = 0x753;
    }
    else {
      iVar2 = 1000;
    }
    unaff_r7 = 1;
    uVar1 = FUN_00480826(((*DAT_00539dbc & 0x3f) * iVar2 + 0xb) / 0xc,DAT_00539dc0,1,1);
  }
  else {
    uVar1 = 7;
  }
  return CONCAT44(unaff_r7,uVar1);
}

