
undefined4 FUN_004810b0(uint param_1,uint param_2,uint *param_3,undefined4 param_4)

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
      iVar3 = FUN_00480ed8(*param_3,&local_24,&local_28);
      if (iVar3 != 0) {
        return 6;
      }
      unaff_r5 = DAT_00481768 + local_24 * 4;
      if ((param_1 & 0xff) == 1) {
        unaff_r5 = unaff_r5 + 0x1c;
      }
    }
    uVar4 = FUN_00473940();
    param_2 = param_2 & 0xff;
    if (param_2 == 0) {
      *unaff_r5 = *unaff_r5 & ~local_28;
      if ((param_1 & 0xff) == 2) {
        unaff_r5[0x1c] = unaff_r5[0x1c] & ~local_28;
      }
    }
    else if (param_2 == 2) {
      if ((param_1 & 0xff) != 1) {
        *DAT_00481768 = *DAT_00481768 & ~*param_3;
        *DAT_0048176c = *DAT_0048176c & ~param_3[1];
        *DAT_00481770 = *DAT_00481770 & ~param_3[2];
        *DAT_00481774 = *DAT_00481774 & ~param_3[3];
        *DAT_00481778 = *DAT_00481778 & ~param_3[4];
        *DAT_0048177c = *DAT_0048177c & ~param_3[5];
        *DAT_00481780 = *DAT_00481780 & ~param_3[6];
      }
      if ((param_1 & 0xff) != 0) {
        *DAT_00481784 = *DAT_00481784 & ~*param_3;
        *DAT_00481788 = *DAT_00481788 & ~param_3[1];
        *DAT_0048178c = *DAT_0048178c & ~param_3[2];
        *DAT_00481790 = *DAT_00481790 & ~param_3[3];
        *DAT_00481794 = *DAT_00481794 & ~param_3[4];
        *DAT_00481798 = *DAT_00481798 & ~param_3[5];
        *DAT_0048179c = *DAT_0048179c & ~param_3[6];
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
        *DAT_00481768 = *param_3 | *DAT_00481768;
        *DAT_0048176c = param_3[1] | *DAT_0048176c;
        *DAT_00481770 = param_3[2] | *DAT_00481770;
        *DAT_00481774 = param_3[3] | *DAT_00481774;
        *DAT_00481778 = param_3[4] | *DAT_00481778;
        *DAT_0048177c = param_3[5] | *DAT_0048177c;
        *DAT_00481780 = param_3[6] | *DAT_00481780;
      }
      if ((param_1 & 0xff) != 0) {
        *DAT_00481784 = *param_3 | *DAT_00481784;
        *DAT_00481788 = param_3[1] | *DAT_00481788;
        *DAT_0048178c = param_3[2] | *DAT_0048178c;
        *DAT_00481790 = param_3[3] | *DAT_00481790;
        *DAT_00481794 = param_3[4] | *DAT_00481794;
        *DAT_00481798 = param_3[5] | *DAT_00481798;
        *DAT_0048179c = param_3[6] | *DAT_0048179c;
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

