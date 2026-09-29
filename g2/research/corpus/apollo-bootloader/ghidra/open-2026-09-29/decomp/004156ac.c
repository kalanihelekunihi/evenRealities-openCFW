
void FUN_004156ac(undefined4 *param_1,undefined4 *param_2,uint param_3)

{
  uint uVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  undefined4 *puVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  
  while (uVar1 = param_3 - 0x10, 0xf < param_3) {
    uVar6 = *param_2;
    uVar7 = param_2[1];
    uVar8 = param_2[2];
    uVar9 = param_2[3];
    param_2 = param_2 + 4;
    *param_1 = uVar6;
    param_1[1] = uVar7;
    param_1[2] = uVar8;
    param_1[3] = uVar9;
    param_1 = param_1 + 4;
    param_3 = uVar1;
  }
  if ((uVar1 & 8) != 0) {
    uVar6 = *param_2;
    uVar7 = param_2[1];
    param_2 = param_2 + 2;
    *param_1 = uVar6;
    param_1[1] = uVar7;
    param_1 = param_1 + 2;
  }
  puVar2 = param_1;
  puVar4 = param_2;
  if ((int)(param_3 << 0x1d) < 0) {
    puVar4 = param_2 + 1;
    puVar2 = param_1 + 1;
    *param_1 = *param_2;
  }
  puVar3 = puVar2;
  puVar5 = puVar4;
  if ((uVar1 & 2) != 0) {
    puVar5 = (undefined4 *)((int)puVar4 + 2);
    puVar3 = (undefined4 *)((int)puVar2 + 2);
    *(undefined2 *)puVar2 = *(undefined2 *)puVar4;
  }
  if ((int)(param_3 << 0x1f) < 0) {
    *(undefined1 *)puVar3 = *(undefined1 *)puVar5;
  }
  return;
}

