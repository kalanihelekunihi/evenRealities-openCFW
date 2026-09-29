
undefined8 FUN_0041f358(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  bool bVar2;
  uint *puVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  
  puVar3 = DAT_0041f4d4;
  uVar8 = *DAT_0041f4d4;
  uVar6 = param_1 & 0xf;
  uVar7 = uVar8 & 0xf;
  uVar4 = FUN_0041f340(uVar6);
  uVar5 = FUN_0041f340(uVar7);
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
    clock_request(uVar4 & 0xff,0x32);
  }
  *puVar3 = param_1;
  if (((bVar2) && (uVar7 != 0)) && (uVar7 < 7)) {
    clock_release(uVar5 & 0xff,0x32);
  }
  *DAT_0041f4d8 = 1;
  return CONCAT44(param_4,uVar8);
}

