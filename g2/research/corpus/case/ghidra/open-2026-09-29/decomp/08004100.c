
undefined4 case_configure_pin_policy(int *param_1,uint *param_2)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  
  uVar5 = 0;
  uVar6 = 0;
  if ((char)param_1[0x15] == '\x01') {
    return 2;
  }
  *(undefined1 *)(param_1 + 0x15) = 1;
  iVar1 = case_status_word2_bit2(*param_1);
  if (iVar1 != 0) {
    param_1[0x16] = param_1[0x16] | 0x20;
    uVar5 = 1;
    goto LAB_0800412c;
  }
  if (param_2[1] == 2) {
    if ((param_1[4] == -0x80000000) || (param_1[4] == -0x7ffffffc)) {
      *(uint *)(*param_1 + 0x28) = *(uint *)(*param_1 + 0x28) & ~(*param_2 & 0x7ffff);
    }
    uVar3 = *param_2;
    if (-1 < (int)uVar3) goto LAB_0800412c;
    if (uVar3 == DAT_08004310) {
      uVar3 = uVar3 << 0xb;
      uVar4 = DAT_08004310;
    }
    else if (uVar3 == DAT_0800431c) {
      uVar3 = uVar3 << 10;
      uVar4 = DAT_0800431c;
    }
    else {
      if (uVar3 != DAT_08004320) goto LAB_0800412c;
      uVar3 = uVar3 << 9;
      uVar4 = DAT_08004320;
    }
    uVar3 = *DAT_0800430c & 0x1c00000 & ~uVar3;
  }
  else {
    if ((param_1[4] == -0x80000000) || (param_1[4] == -0x7ffffffc)) {
      iVar1 = *param_1;
      uVar3 = *(uint *)(iVar1 + 0x28) | *param_2 & 0x7ffff;
LAB_0800423a:
      *(uint *)(iVar1 + 0x28) = uVar3;
    }
    else {
      uVar4 = param_2[1] & 0x1f;
      uVar3 = *param_2;
      if ((uVar3 & 0x7ffff) == 0) {
        uVar3 = (uVar3 & 0x7fffffff) >> 0x1a;
      }
      else if ((uVar3 & 1) == 0) {
        if ((int)(uVar3 << 0x1e) < 0) {
          uVar3 = 1;
        }
        else if ((int)(uVar3 << 0x1d) < 0) {
          uVar3 = 2;
        }
        else if ((int)(uVar3 << 0x1c) < 0) {
          uVar3 = 3;
        }
        else if ((int)(uVar3 << 0x1b) < 0) {
          uVar3 = 4;
        }
        else if ((int)(uVar3 << 0x1a) < 0) {
          uVar3 = 5;
        }
        else if ((int)(uVar3 << 0x19) < 0) {
          uVar3 = 6;
        }
        else if ((int)(uVar3 << 0x18) < 0) {
          uVar3 = 7;
        }
        else if ((int)(uVar3 << 0x17) < 0) {
          uVar3 = 8;
        }
        else if ((int)(uVar3 << 0x16) < 0) {
          uVar3 = 9;
        }
        else if ((int)(uVar3 << 0x15) < 0) {
          uVar3 = 10;
        }
        else if ((int)(uVar3 << 0x14) < 0) {
          uVar3 = 0xb;
        }
        else if ((int)(uVar3 << 0x13) < 0) {
          uVar3 = 0xc;
        }
        else if ((int)(uVar3 << 0x12) < 0) {
          uVar3 = 0xd;
        }
        else if ((int)(uVar3 << 0x11) < 0) {
          uVar3 = 0xe;
        }
        else if ((int)(uVar3 << 0x10) < 0) {
          uVar3 = 0xf;
        }
        else if ((int)(uVar3 << 0xf) < 0) {
          uVar3 = 0x10;
        }
        else if ((int)(uVar3 << 0xe) < 0) {
          uVar3 = 0x11;
        }
        else {
          if (-1 < (int)(uVar3 << 0xd)) goto LAB_0800420a;
          uVar3 = 0x12;
        }
      }
      else {
LAB_0800420a:
        uVar3 = 0;
      }
      param_1[0x18] = param_1[0x18] & ~(0xf << uVar4) | uVar3 << uVar4;
      if ((param_2[1] >> 2) + 1 <= (uint)param_1[7]) {
        iVar1 = *param_1;
        uVar3 = param_2[1] & 0x1f;
        uVar3 = *(uint *)(iVar1 + 0x28) & ~(0xf << uVar3) |
                ((*param_2 & 0x3fffffff) >> 0x1a) << uVar3;
        goto LAB_0800423a;
      }
    }
    *(uint *)(*param_1 + 0x14) =
         *(uint *)(*param_1 + 0x14) & ~(*param_2 << 8) | *param_2 << 8 & param_2[2] & 0x7ffffff;
    uVar2 = *param_2;
    if (-1 < (int)uVar2) goto LAB_0800412c;
    uVar3 = *DAT_0800430c & 0x1c00000;
    if ((uVar2 == DAT_08004310) && (-1 < (int)(uVar3 << 8))) {
      case_control_word0_replace_field22
                (DAT_0800430c,uVar3 | uVar2 << 0xb,DAT_0800430c,uVar3 << 8,uVar6);
      iVar1 = __aeabi_uidiv(*DAT_08004318,DAT_08004314);
      for (iVar1 = (iVar1 + 1) * 0xc; iVar1 != 0; iVar1 = iVar1 + -1) {
      }
      goto LAB_0800412c;
    }
    if ((uVar2 == DAT_0800431c) && (-1 < (int)(uVar3 << 7))) {
      uVar2 = uVar2 << 10;
      uVar4 = uVar3 << 7;
    }
    else {
      if ((uVar2 != DAT_08004320) || ((int)(uVar3 << 9) < 0)) goto LAB_0800412c;
      uVar2 = DAT_08004320 << 9;
      uVar4 = DAT_08004320;
    }
    uVar3 = uVar3 | uVar2;
  }
  case_control_word0_replace_field22(DAT_0800430c,uVar3,DAT_0800430c,uVar4,uVar6);
LAB_0800412c:
  *(undefined1 *)(param_1 + 0x15) = 0;
  return uVar5;
}

