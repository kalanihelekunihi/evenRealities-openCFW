
undefined8 FUN_0048d588(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  bool bVar2;
  uint *puVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  
  puVar3 = DAT_0048d704;
  uVar8 = *DAT_0048d704;
  uVar6 = param_1 & 0xf;
  uVar7 = uVar8 & 0xf;
  uVar4 = FUN_0048d570(uVar6);
  uVar5 = FUN_0048d570(uVar7);
  if ((param_1 & 0xc0000000) == 0) {
    if ((uVar8 & 0xc0000000) == 0) {
      if (uVar4 == uVar5) {
        bVar1 = false;
        bVar2 = false;
      }
      else {
        bVar1 = true;
        bVar2 = true;
      }
    }
    else {
      bVar1 = true;
      bVar2 = false;
    }
  }
  else {
    bVar1 = false;
    bVar2 = true;
  }
  if (((bVar1) && (uVar6 != 0)) && (uVar6 < 7)) {
    FUN_004c44bc(uVar4 & 0xff,0x32);
  }
  *puVar3 = param_1;
  if (((bVar2) && (uVar7 != 0)) && (uVar7 < 7)) {
    FUN_004c4530(uVar5 & 0xff,0x32);
  }
  *DAT_0048d708 = 1;
  return CONCAT44(param_4,uVar8);
}

