
void FUN_00522db4(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                 undefined4 param_5,undefined4 param_6,undefined4 param_7,undefined4 param_8)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  undefined4 *puVar10;
  
  uVar2 = FUN_005242cc();
  uVar3 = FUN_005242cc(param_2);
  uVar4 = FUN_005242cc(param_3);
  uVar5 = FUN_005242cc(param_4);
  uVar6 = FUN_005242cc(param_5);
  uVar7 = FUN_005242cc(param_6);
  uVar8 = FUN_005242cc(param_7);
  uVar9 = FUN_005242cc(param_8);
  puVar10 = (undefined4 *)FUN_00514aec(9);
  if (puVar10 != (undefined4 *)0x0) {
    *puVar10 = 0x120;
    puVar10[2] = 0x124;
    puVar10[4] = 0x130;
    puVar10[6] = 0x134;
    puVar10[8] = 0x140;
    puVar10[10] = 0x144;
    puVar10[0xc] = 0x150;
    puVar10[0xe] = 0x154;
    uVar1 = DAT_005232cc;
    puVar10[1] = uVar2;
    puVar10[3] = uVar3;
    puVar10[5] = uVar4;
    puVar10[7] = uVar5;
    puVar10[9] = uVar6;
    puVar10[0xb] = uVar7;
    puVar10[0xd] = uVar8;
    puVar10[0xf] = uVar9;
    puVar10[0x10] = uVar1;
    puVar10[0x11] = *(uint *)(*DAT_005232d0 + 0x18) | 5;
  }
  return;
}

