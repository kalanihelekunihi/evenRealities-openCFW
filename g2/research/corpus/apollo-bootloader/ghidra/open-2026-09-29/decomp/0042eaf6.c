
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 hw_channel_config_42eaf6(uint *param_1,uint param_2,byte *param_3)

{
  undefined4 uVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != _DAT_0042f17c)) {
    uVar1 = 2;
  }
  else if (param_2 < 8) {
    if ((*(uint *)(param_3 + 4) < 0x20) || (0x3f < *(uint *)(param_3 + 4))) {
      uVar1 = 6;
    }
    else {
      *(uint *)(_DAT_0042f184 + param_2 * 4) =
           (*param_3 & 7) << 0x18 | (*(uint *)(param_3 + 4) & 0x3f) << 0x12 |
           (param_3[8] & 3) << 0x10 | (param_3[9] & 0xf) << 8 | (uint)param_3[10] << 1 |
           (uint)param_3[0xb];
      *_DAT_0042f154 = *_DAT_0042f154 + 1;
      uVar1 = 0;
    }
  }
  else {
    uVar1 = 5;
  }
  return uVar1;
}

