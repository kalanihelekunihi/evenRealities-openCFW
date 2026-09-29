
uint FUN_005dd832(int *param_1,uint *param_2)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  byte *pbVar7;
  uint uVar8;
  
  uVar1 = 0;
  iVar3 = param_1[4];
  uVar2 = (uint)*(byte *)(iVar3 + 0x200f) |
          (uint)*(byte *)(iVar3 + 0x200d) << 0x10 | (uint)*(byte *)(iVar3 + 0x200c) << 0x18 |
          (uint)*(byte *)(iVar3 + 0x200e) << 8;
  if (*param_2 == 0xffffffff) {
    uVar1 = 0;
  }
  else {
    uVar6 = *param_2 + 1;
    pbVar7 = (byte *)(iVar3 + 0x2010);
    for (; uVar5 = 0, uVar2 != 0; uVar2 = uVar2 - 1) {
      uVar4 = (uint)pbVar7[3] |
              (uint)pbVar7[1] << 0x10 | (uint)*pbVar7 << 0x18 | (uint)pbVar7[2] << 8;
      uVar8 = (uint)pbVar7[0xb] |
              (uint)pbVar7[9] << 0x10 | (uint)pbVar7[8] << 0x18 | (uint)pbVar7[10] << 8;
      if (uVar6 < uVar4) {
        uVar6 = uVar4;
      }
      while( true ) {
        if ((((uint)pbVar7[7] |
             (uint)pbVar7[5] << 0x10 | (uint)pbVar7[4] << 0x18 | (uint)pbVar7[6] << 8) < uVar6) ||
           (uVar4 + (-1 - uVar6) < uVar8)) goto LAB_005dd8aa;
        uVar1 = (uVar6 + uVar8) - uVar4;
        if (uVar1 != 0) break;
        if (uVar6 == 0xffffffff) goto LAB_005dd92e;
        uVar6 = uVar6 + 1;
      }
      uVar5 = uVar6;
      if (uVar1 < *(uint *)(*param_1 + 0x10)) break;
      uVar1 = 0;
LAB_005dd8aa:
      pbVar7 = pbVar7 + 0xc;
    }
LAB_005dd92e:
    *param_2 = uVar5;
  }
  return uVar1;
}

