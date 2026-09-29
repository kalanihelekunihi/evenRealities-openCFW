
undefined4 FUN_0041da84(uint param_1,uint param_2,uint *param_3,undefined4 param_4)

{
  bool bVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  uint *unaff_r5;
  uint local_28;
  uint local_24;
  uint *local_20;
  undefined4 uStack_1c;
  
  if (param_3 == (uint *)0x0) {
    uVar2 = 6;
  }
  else if ((param_2 & 0xff) < 4) {
    local_28 = param_1;
    local_24 = param_2;
    local_20 = param_3;
    uStack_1c = param_4;
    if ((param_2 & 0xff) < 2) {
      if (0xdf < *param_3) {
        return 5;
      }
      iVar3 = FUN_0041d8f8(*param_3,&local_24,&local_28);
      if (iVar3 != 0) {
        return 6;
      }
      unaff_r5 = DAT_0041e138 + local_24 * 4;
      if ((param_1 & 0xff) == 1) {
        unaff_r5 = unaff_r5 + 0x1c;
      }
    }
    uVar4 = critical_save();
    param_2 = param_2 & 0xff;
    if (param_2 == 0) {
      *unaff_r5 = *unaff_r5 & ~local_28;
      if ((param_1 & 0xff) == 2) {
        unaff_r5[0x1c] = unaff_r5[0x1c] & ~local_28;
      }
    }
    else if (param_2 == 2) {
      if ((param_1 & 0xff) != 1) {
        *DAT_0041e138 = *DAT_0041e138 & ~*param_3;
        *DAT_0041e13c = *DAT_0041e13c & ~param_3[1];
        *DAT_0041e140 = *DAT_0041e140 & ~param_3[2];
        *DAT_0041e144 = *DAT_0041e144 & ~param_3[3];
        *DAT_0041e148 = *DAT_0041e148 & ~param_3[4];
        *DAT_0041e14c = *DAT_0041e14c & ~param_3[5];
        *DAT_0041e150 = *DAT_0041e150 & ~param_3[6];
      }
      if ((param_1 & 0xff) != 0) {
        *DAT_0041e154 = *DAT_0041e154 & ~*param_3;
        *DAT_0041e158 = *DAT_0041e158 & ~param_3[1];
        *DAT_0041e15c = *DAT_0041e15c & ~param_3[2];
        *DAT_0041e160 = *DAT_0041e160 & ~param_3[3];
        *DAT_0041e164 = *DAT_0041e164 & ~param_3[4];
        *DAT_0041e168 = *DAT_0041e168 & ~param_3[5];
        *DAT_0041e16c = *DAT_0041e16c & ~param_3[6];
      }
    }
    else if (param_2 < 2) {
      *unaff_r5 = *unaff_r5 | local_28;
      if ((param_1 & 0xff) == 2) {
        unaff_r5[0x1c] = unaff_r5[0x1c] | local_28;
      }
    }
    else if (param_2 == 3) {
      if ((param_1 & 0xff) != 1) {
        *DAT_0041e138 = *param_3 | *DAT_0041e138;
        *DAT_0041e13c = param_3[1] | *DAT_0041e13c;
        *DAT_0041e140 = param_3[2] | *DAT_0041e140;
        *DAT_0041e144 = param_3[3] | *DAT_0041e144;
        *DAT_0041e148 = param_3[4] | *DAT_0041e148;
        *DAT_0041e14c = param_3[5] | *DAT_0041e14c;
        *DAT_0041e150 = param_3[6] | *DAT_0041e150;
      }
      if ((param_1 & 0xff) != 0) {
        *DAT_0041e154 = *param_3 | *DAT_0041e154;
        *DAT_0041e158 = param_3[1] | *DAT_0041e158;
        *DAT_0041e15c = param_3[2] | *DAT_0041e15c;
        *DAT_0041e160 = param_3[3] | *DAT_0041e160;
        *DAT_0041e164 = param_3[4] | *DAT_0041e164;
        *DAT_0041e168 = param_3[5] | *DAT_0041e168;
        *DAT_0041e16c = param_3[6] | *DAT_0041e16c;
      }
    }
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((uVar4 & 1) == 1);
    }
    uVar2 = 0;
  }
  else {
    uVar2 = 6;
  }
  return uVar2;
}

