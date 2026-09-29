
void case_release_pins(uint *param_1,uint param_2)

{
  uint *puVar1;
  uint *puVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  
  for (uVar4 = 0; puVar2 = DAT_08004cec, param_2 >> (uVar4 & 0xff) != 0; uVar4 = uVar4 + 1) {
    uVar5 = 1 << (uVar4 & 0xff);
    uVar3 = uVar5 & param_2;
    if (uVar3 != 0) {
      uVar7 = uVar4 & 0xfffffffc;
      iVar8 = (uVar4 & 3) << 3;
      uVar6 = 0xf << iVar8;
      if (param_1 == (uint *)0x50000000) {
        iVar9 = 0;
      }
      else if (param_1 == DAT_08004cf0) {
        iVar9 = 1;
      }
      else if (param_1 == DAT_08004cf4) {
        iVar9 = 2;
      }
      else if (param_1 == DAT_08004cf8) {
        iVar9 = 3;
      }
      else if (param_1 == DAT_08004cfc) {
        iVar9 = 4;
      }
      else {
        iVar9 = 5;
      }
      if (iVar9 << iVar8 == (uVar6 & *(uint *)((int)DAT_08004cec + uVar7 + 0x60))) {
        DAT_08004cec[0x20] = DAT_08004cec[0x20] & ~uVar3;
        puVar2[0x21] = puVar2[0x21] & ~uVar3;
        puVar1 = DAT_08004cec;
        DAT_08004cec[1] = DAT_08004cec[1] & ~uVar3;
        *puVar1 = *puVar1 & ~uVar3;
        *(uint *)((int)puVar2 + uVar7 + 0x60) = *(uint *)((int)puVar2 + uVar7 + 0x60) & ~uVar6;
      }
      uVar3 = 3 << ((uVar4 & 0x7f) << 1);
      *param_1 = *param_1 | uVar3;
      param_1[(uVar4 >> 3) + 8] = param_1[(uVar4 >> 3) + 8] & ~(0xf << ((uVar4 & 7) << 2));
      param_1[2] = param_1[2] & ~uVar3;
      param_1[1] = param_1[1] & ~uVar5;
      param_1[3] = param_1[3] & ~uVar3;
    }
  }
  return;
}

