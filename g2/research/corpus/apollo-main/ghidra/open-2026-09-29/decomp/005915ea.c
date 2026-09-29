
undefined8
algo_front_data_preprocess(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint *puVar2;
  uint *puVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  uint uVar7;
  uint uVar8;
  undefined8 uVar9;
  uint uVar10;
  
  iVar5 = DAT_00591cf4;
  if (((param_1 == 0) || ((param_2 & 3) != 0)) || (0xc80 < param_2)) {
    uVar10 = param_2;
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      uVar10 = 0x2b;
      FUN_0043d574(1,DAT_00591ca4,DAT_00591ca0,DAT_00591c94,0x2b,DAT_00591c90,param_2);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00591c98,DAT_00591c98,param_2);
    }
    param_2 = uVar10;
    uVar6 = 0xffffffff;
  }
  else {
    FUN_0043c0e4(DAT_00591cf4,0x640,0,param_4,param_2,param_3,param_4);
    iVar4 = DAT_00591cf0;
    FUN_0043c0e4(DAT_00591cf0,0x640,0);
    iVar1 = DAT_00591c9c;
    FUN_0043c0e4(DAT_00591c9c,0x640,0);
    puVar2 = DAT_00591cb0;
    *DAT_00591cb0 = 0;
    puVar2[1] = 0;
    puVar3 = DAT_00591cc0;
    *DAT_00591cc0 = 0;
    puVar3[1] = 0;
    for (uVar10 = 0; uVar10 < 800; uVar10 = uVar10 + 1) {
      *(undefined2 *)(iVar5 + uVar10 * 2) = *(undefined2 *)(param_1 + uVar10 * 4);
      *(undefined2 *)(iVar4 + uVar10 * 2) = *(undefined2 *)(param_1 + uVar10 * 4 + 2);
      *(short *)(iVar1 + uVar10 * 2) =
           *(short *)(iVar4 + uVar10 * 2) / 2 + *(short *)(iVar5 + uVar10 * 2) / 2;
      uVar8 = *puVar2;
      uVar7 = (int)*(short *)(iVar5 + uVar10 * 2) * (int)*(short *)(iVar5 + uVar10 * 2);
      *puVar2 = uVar8 + uVar7;
      puVar2[1] = ((int)uVar7 >> 0x1f) + puVar2[1] + (uint)CARRY4(uVar8,uVar7);
      uVar8 = *puVar3;
      uVar7 = (int)*(short *)(iVar4 + uVar10 * 2) * (int)*(short *)(iVar4 + uVar10 * 2);
      *puVar3 = uVar8 + uVar7;
      puVar3[1] = ((int)uVar7 >> 0x1f) + puVar3[1] + (uint)CARRY4(uVar8,uVar7);
    }
    uVar9 = FUN_0047cc60(*puVar2,puVar2[1],800,0);
    *(undefined8 *)puVar2 = uVar9;
    uVar9 = FUN_0047cc60(*puVar3,puVar3[1],800,0);
    *(undefined8 *)puVar3 = uVar9;
    uVar6 = 0;
  }
  return CONCAT44(param_2,uVar6);
}

