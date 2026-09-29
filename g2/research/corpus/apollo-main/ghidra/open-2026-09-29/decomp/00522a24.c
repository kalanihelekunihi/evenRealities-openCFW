
void FUN_00522a24(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                 undefined4 param_5,undefined4 param_6)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined4 *puVar8;
  uint uVar9;
  
  uVar2 = FUN_005242cc();
  uVar3 = FUN_005242cc(param_2);
  uVar4 = FUN_005242cc(param_3);
  uVar5 = FUN_005242cc(param_4);
  uVar6 = FUN_005242cc(param_5);
  uVar7 = FUN_005242cc(param_6);
  puVar8 = (undefined4 *)FUN_00514aec(7);
  if (puVar8 != (undefined4 *)0x0) {
    *puVar8 = 0x120;
    puVar8[2] = 0x124;
    puVar8[4] = 0x130;
    puVar8[6] = 0x134;
    puVar8[8] = 0x140;
    puVar8[10] = 0x144;
    uVar1 = DAT_005232cc;
    puVar8[1] = uVar2;
    puVar8[3] = uVar3;
    puVar8[5] = uVar4;
    puVar8[7] = uVar5;
    puVar8[9] = uVar6;
    puVar8[0xb] = uVar7;
    puVar8[0xc] = uVar1;
    uVar9 = *(uint *)(*DAT_005232d0 + 0x18);
    if ((int)(uVar9 << 7) < 0) {
      uVar9 = uVar9 | 0x800000;
    }
    else {
      uVar9 = uVar9 & 0xff7fffff;
    }
    puVar8[0xd] = uVar9 | 4;
  }
  return;
}

