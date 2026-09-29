
undefined4 FUN_0053ebbc(float param_1,float param_2,float param_3,float param_4,float param_5)

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
  undefined4 in_r3;
  float fVar10;
  float fVar11;
  float fVar12;
  
  fVar10 = param_3 - param_1;
  if ((int)((uint)(param_5 < 1.0) << 0x1f) < 0) {
    param_5 = 1.0;
  }
  fVar11 = fVar10;
  if ((int)((uint)(fVar10 < 0.0) << 0x1f) < 0) {
    fVar11 = -fVar10;
  }
  fVar12 = DAT_0053ecf8;
  if (-1 < (int)((uint)(fVar11 < 0.5) << 0x1f)) {
    uVar1 = FUN_00524260((param_4 - param_2) / fVar10);
    fVar10 = (float)FUN_0052405c(uVar1);
    fVar11 = (float)FUN_00524130(uVar1);
    fVar12 = fVar11 * param_5 * -0.5;
    param_5 = fVar10 * param_5;
  }
  param_5 = param_5 * 0.5;
  uVar1 = FUN_0052266e(1,1,1,1);
  uVar2 = FUN_005242cc(param_2 - fVar12);
  uVar3 = FUN_005242cc(param_1 - param_5);
  uVar4 = FUN_005242cc(param_4 - fVar12);
  uVar5 = FUN_005242cc(param_3 - param_5);
  uVar6 = FUN_005242cc(param_4 + fVar12);
  uVar7 = FUN_005242cc(param_3 + param_5);
  uVar8 = FUN_005242cc(param_2 + fVar12);
  uVar9 = FUN_005242cc(param_1 + param_5);
  FUN_00522e9c(uVar9,uVar8,uVar7,uVar6,uVar5,uVar4,uVar3,uVar2);
  FUN_005226b2(uVar1);
  return in_r3;
}

