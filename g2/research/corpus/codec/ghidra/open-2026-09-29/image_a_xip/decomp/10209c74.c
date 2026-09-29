
uint gx8002_uart_transmit_dma(int param_1,uint param_2,int param_3,int param_4)

{
  uint uVar1;
  uint uVar2;
  int unaff_r4;
  int iVar3;
  uint uVar4;
  uint unaff_r5;
  uint unaff_r6;
  uint uVar5;
  uint unaff_r7;
  uint uVar6;
  uint uVar7;
  uint in_r12;
  uint uVar8;
  
  uVar7 = (unaff_r6 & 0x7fff) * param_4;
  uVar8 = (param_2 | in_r12) >> 0x10 | (unaff_r4 - param_4 * unaff_r7) * 0x10000;
  uVar1 = param_3 << (unaff_r5 & 0x3f);
  iVar3 = param_4;
  if (uVar8 < uVar7) {
    uVar8 = uVar8 + unaff_r6;
    iVar3 = param_4 + -1;
    if ((unaff_r6 <= uVar8) && (uVar8 < uVar7)) {
      iVar3 = param_4 + -2;
      uVar8 = uVar8 + unaff_r6;
    }
  }
  uVar4 = (uVar8 - uVar7) / unaff_r7;
  uVar6 = (unaff_r6 & 0x7fff) * uVar4;
  uVar8 = (param_2 | in_r12) & 0x7fff | ((uVar8 - uVar7) - uVar4 * unaff_r7) * 0x10000;
  uVar7 = uVar4;
  if (uVar8 < uVar6) {
    uVar8 = uVar8 + unaff_r6;
    uVar7 = uVar4 - 1;
    if ((unaff_r6 <= uVar8) && (uVar8 < uVar6)) {
      uVar7 = uVar4 - 2;
      uVar8 = uVar8 + unaff_r6;
    }
  }
  uVar2 = iVar3 << 0x10 | uVar7;
  uVar4 = uVar1 & 0x7fff;
  uVar1 = uVar1 >> 0x10;
  uVar5 = (uVar7 & 0x7fff) * uVar4;
  uVar7 = (uVar5 >> 0x10) + uVar1 * (uVar7 & 0x7fff) + (uVar2 >> 0x10) * uVar4;
  uVar1 = uVar1 * (uVar2 >> 0x10) + (uVar7 >> 0x10);
  if ((uVar1 <= uVar8 - uVar6) &&
     ((uVar8 - uVar6 != uVar1 ||
      (uVar7 * 0x10000 + (uVar5 & 0x7fff) <= (uint)(param_1 << (unaff_r5 & 0x3f)))))) {
    return uVar2;
  }
  return uVar2 - 1;
}

