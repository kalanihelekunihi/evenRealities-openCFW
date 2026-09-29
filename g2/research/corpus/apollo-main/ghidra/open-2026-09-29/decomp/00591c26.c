
undefined4 service_algo_energy_window_update(int param_1,uint param_2)

{
  int *piVar1;
  undefined4 uVar2;
  uint uVar3;
  int iVar4;
  int extraout_r2;
  int extraout_r3;
  uint uVar5;
  uint uVar6;
  bool bVar7;
  undefined8 uVar8;
  
  piVar1 = DAT_00591d00;
  if ((param_1 == 0) || (param_2 == 0)) {
    uVar2 = 0xffffffff;
  }
  else {
    uVar3 = 0;
    iVar4 = 0;
    for (uVar6 = 0; uVar6 < param_2 >> 1; uVar6 = uVar6 + 1) {
      uVar5 = (int)*(short *)(param_1 + uVar6 * 2) * (int)*(short *)(param_1 + uVar6 * 2);
      bVar7 = CARRY4(uVar3,uVar5);
      uVar3 = uVar3 + uVar5;
      iVar4 = iVar4 + ((int)uVar5 >> 0x1f) + (uint)bVar7;
    }
    uVar8 = FUN_0047cc60(uVar3,iVar4,param_2 >> 1,0);
    *(undefined8 *)(DAT_00591d04 + *piVar1 * 8) = uVar8;
    FUN_0047cc60(*piVar1 + 1,(piVar1[1] + 1) - (uint)(*piVar1 != -1),10,0);
    *piVar1 = extraout_r2;
    piVar1[1] = extraout_r3;
    uVar2 = 0;
  }
  return uVar2;
}

