
int am_hal_mspi_power_control(uint *param_1,byte param_2,char param_3)

{
  int iVar1;
  
  iVar1 = DAT_00426c0c;
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_00426c04)) {
    return 2;
  }
  if (param_2 == 0) {
    if ((param_3 != '\0') && ((char)param_1[0x218] == '\0')) {
      return 7;
    }
    FUN_0041bf84(param_1[1] + 0x10 & 0xff);
    if (param_3 == '\0') {
      *(undefined1 *)((int)param_1 + 0x8c9) = 4;
      iVar1 = clock_request(4,param_1[1] + 0x10 & 0xff);
      if (iVar1 != 0) {
        return iVar1;
      }
      mspi_clkgen_ctrl(param_1[1],1,1,8);
    }
    else {
      if (*(char *)((int)param_1 + 0x8c9) == '\a') {
        return 7;
      }
      iVar1 = clock_request(*(undefined1 *)((int)param_1 + 0x8c9),param_1[1] + 0x10 & 0xff);
      if (iVar1 != 0) {
        return iVar1;
      }
      mspi_clkgen_ctrl(param_1[1],1,0,0);
      iVar1 = DAT_00426c0c;
      *(uint *)(DAT_00426c0c + param_1[1] * 0x1000 + 0x80) = param_1[0x219];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x84) = param_1[0x21a];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x88) = param_1[0x21b];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x8c) = param_1[0x21c];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x90) = param_1[0x21d];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x94) = param_1[0x21e];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x98) = param_1[0x21f];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x9c) = param_1[0x220];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0xa0) = param_1[0x221];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0xa4) = param_1[0x222];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0xa8) = param_1[0x223];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x30) = param_1[0x224];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x44) = param_1[0x225];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x48) = param_1[0x226];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x4c) = param_1[0x227];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x2a8) = param_1[0x229];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x2b8) = param_1[0x22a];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x2c0) = param_1[0x22b];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x2c4) = param_1[0x22c];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x200) = param_1[0x22d];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x2b4) = (uint)(byte)param_1[0x22e];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x114) = param_1[0x22f];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x118) = param_1[0x230];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x20) = param_1[0x231];
      *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x2a0) = param_1[0x228] & 0xfffffffe;
      if ((int)((uint)(byte)param_1[0x228] << 0x1f) < 0) {
        FUN_00423f8e(param_1);
      }
      *(undefined1 *)(param_1 + 0x218) = 0;
    }
  }
  else {
    if ((param_2 != 2) && (1 < param_2)) {
      return 6;
    }
    if ((param_1[0x210] != 0) || (param_1[8] != 0)) {
      return 3;
    }
    if (param_3 != '\0') {
      param_1[0x219] = *(uint *)(DAT_00426c0c + param_1[1] * 0x1000 + 0x80);
      param_1[0x21a] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x84);
      param_1[0x21b] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x88);
      param_1[0x21c] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x8c);
      param_1[0x21d] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x90);
      param_1[0x21e] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x94);
      param_1[0x21f] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x98);
      param_1[0x220] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x9c);
      param_1[0x221] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0xa0);
      param_1[0x222] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0xa4);
      param_1[0x223] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0xa8);
      param_1[0x224] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x30);
      param_1[0x225] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x44);
      param_1[0x226] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x48);
      param_1[0x227] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x4c);
      param_1[0x229] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x2a8);
      param_1[0x22a] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x2b8);
      param_1[0x22b] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x2c0);
      param_1[0x22c] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x2c4);
      param_1[0x22d] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x200);
      param_1[0x22e] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x2b0);
      param_1[0x22f] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x114);
      param_1[0x230] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x118);
      param_1[0x231] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x20);
      param_1[0x228] = *(uint *)(iVar1 + param_1[1] * 0x1000 + 0x2a0);
      if (*(int *)(iVar1 + param_1[1] * 0x1000 + 0x2a0) << 0x1f < 0) {
        cq_disable(param_1);
      }
      *(undefined1 *)(param_1 + 0x218) = 1;
    }
    am_hal_mspi_interrupt_disable(param_1,0x1fff);
    if (*(int *)(DAT_00426c0c + param_1[1] * 0x1000 + 0x90) << 0x1f < 0) {
      delay_us(param_1[0x233]);
    }
    FUN_0041c17a(param_1[1] + 0x10 & 0xff);
    mspi_clkgen_ctrl(param_1[1],0,0,0);
    iVar1 = FUN_004223d8(param_1[1] + 0x10 & 0xff);
    if (iVar1 != 0) {
      return iVar1;
    }
  }
  return 0;
}

