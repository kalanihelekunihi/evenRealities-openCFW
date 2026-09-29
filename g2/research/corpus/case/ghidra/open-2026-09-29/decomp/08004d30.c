
void FUN_08004d30(uint *param_1,uint *param_2)

{
  uint *puVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  byte bVar5;
  int iVar6;
  uint *puVar7;
  int iVar8;
  
  for (uVar3 = 0; *param_2 >> (uVar3 & 0xff) != 0; uVar3 = uVar3 + 1) {
    uVar4 = 1 << (uVar3 & 0xff);
    uVar2 = *param_2 & uVar4;
    if (uVar2 != 0) {
      bVar5 = (byte)param_2[1] & 3;
      if ((bVar5 == 1) || (bVar5 == 2)) {
        param_1[2] = param_2[3] << (uVar3 << 1 & 0xff) | param_1[2] & ~(3 << (uVar3 << 1 & 0xff));
        param_1[1] = (((byte)param_2[1] & 0x1f) >> 4) << (uVar3 & 0xff) | param_1[1] & ~uVar4;
      }
      if ((~(byte)param_2[1] & 3) != 0) {
        param_1[3] = param_2[2] << (uVar3 << 1 & 0xff) | param_1[3] & ~(3 << (uVar3 << 1 & 0xff));
      }
      if ((param_2[1] & 3) == 2) {
        iVar6 = (uVar3 & 7) << 2;
        param_1[(uVar3 >> 3) + 8] =
             param_2[4] << iVar6 | param_1[(uVar3 >> 3) + 8] & ~(0xf << iVar6);
      }
      *param_1 = ((byte)param_2[1] & 3) << (uVar3 << 1 & 0xff) |
                 *param_1 & ~(3 << (uVar3 << 1 & 0xff));
      puVar7 = DAT_08004e80;
      if ((param_2[1] & 0x3ffff) >> 0x10 != 0) {
        iVar6 = (uVar3 & 3) << 3;
        if (param_1 == (uint *)0x50000000) {
          iVar8 = 0;
        }
        else if (param_1 == DAT_08004e84) {
          iVar8 = 1;
        }
        else if (param_1 == DAT_08004e88) {
          iVar8 = 2;
        }
        else if (param_1 == DAT_08004e8c) {
          iVar8 = 3;
        }
        else if (param_1 == DAT_08004e90) {
          iVar8 = 4;
        }
        else {
          iVar8 = 5;
        }
        *(uint *)((int)DAT_08004e80 + (uVar3 & 0xfffffffc) + 0x60) =
             iVar8 << iVar6 |
             *(uint *)((int)DAT_08004e80 + (uVar3 & 0xfffffffc) + 0x60) & ~(0xf << iVar6);
        puVar1 = DAT_08004e80;
        uVar4 = *puVar7 & ~uVar2;
        if ((int)(param_2[1] << 0xb) < 0) {
          uVar4 = uVar4 | uVar2;
        }
        *DAT_08004e80 = uVar4;
        uVar4 = puVar1[1] & ~uVar2;
        if ((int)(param_2[1] << 10) < 0) {
          uVar4 = uVar4 | uVar2;
        }
        puVar1[1] = uVar4;
        puVar7 = DAT_08004e80 + 0x20;
        uVar4 = DAT_08004e80[0x21] & ~uVar2;
        if ((int)(param_2[1] << 0xe) < 0) {
          uVar4 = uVar4 | uVar2;
        }
        DAT_08004e80[0x21] = uVar4;
        uVar4 = *puVar7 & ~uVar2;
        if ((int)(param_2[1] << 0xf) < 0) {
          uVar4 = uVar4 | uVar2;
        }
        *puVar7 = uVar4;
      }
    }
  }
  return;
}

