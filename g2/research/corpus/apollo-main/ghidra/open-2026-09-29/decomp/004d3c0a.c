
undefined8 FUN_004d3c0a(uint *param_1)

{
  bool bVar1;
  uint uVar2;
  undefined4 uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  uVar2 = FUN_00473940();
  FUN_004d3b9a();
  uVar6 = *DAT_004d3cd8;
  uVar5 = *DAT_004d3cdc;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar2 & 1) == 1);
  }
  *param_1 = uVar5 >> 0x1f;
  if (*param_1 == 0) {
    uVar4 = FUN_004d3a20((uVar6 & 0x3fffffff) >> 0x18);
    param_1[6] = uVar4;
    uVar4 = FUN_004d3a20((uVar6 & 0x7fffff) >> 0x10);
    param_1[7] = uVar4;
    uVar4 = FUN_004d3a20((uVar6 & 0x7fff) >> 8);
    param_1[8] = uVar4;
    uVar6 = FUN_004d3a20(uVar6 & 0xff);
    param_1[9] = uVar6;
    param_1[2] = (uVar5 & 0x1fffffff) >> 0x1c;
    uVar6 = FUN_004d3a20((uVar5 & 0x7ffffff) >> 0x18);
    param_1[1] = uVar6;
    uVar6 = FUN_004d3a20((uVar5 & 0xffffff) >> 0x10);
    param_1[3] = uVar6;
    uVar6 = FUN_004d3a20((uVar5 & 0x1fff) >> 8);
    param_1[4] = uVar6;
    uVar5 = FUN_004d3a20(uVar5 & 0x3f);
    param_1[5] = uVar5;
    if (*param_1 == 0) {
      uVar3 = 0;
    }
    else {
      uVar3 = 1;
    }
  }
  else {
    uVar3 = 1;
  }
  return CONCAT44(uVar2,uVar3);
}

