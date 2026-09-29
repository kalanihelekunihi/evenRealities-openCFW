
undefined8 FUN_005c55b2(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  int iVar6;
  undefined4 local_20;
  undefined4 uStack_1c;
  undefined4 local_18;
  
  iVar6 = *(int *)(param_1 + 0x2c);
  local_20 = param_2;
  uStack_1c = param_3;
  local_18 = param_4;
  uVar2 = FUN_00452ef8();
  iVar3 = FUN_00452f00(uVar2);
  if (iVar3 == 4) {
    *(undefined4 *)(iVar6 + 0x44) = *(undefined4 *)(iVar6 + 0x40);
    uVar4 = FUN_0043e1be(iVar6);
    iVar3 = FUN_0044d5a4(uVar4);
    if (iVar3 != 0) {
      FUN_0044d510(uVar4,0);
    }
  }
  iVar3 = FUN_00452f00(uVar2);
  if ((iVar3 == 1) || (iVar3 = FUN_00452f00(uVar2), iVar3 == 3)) {
    FUN_00452f5e(uVar2,&uStack_1c);
    uVar2 = FUN_005c5682(iVar6,local_18);
    *(undefined4 *)(iVar6 + 0x40) = uVar2;
    *(undefined4 *)(iVar6 + 0x44) = *(undefined4 *)(iVar6 + 0x40);
  }
  FUN_005c4c44(iVar6);
  if (*(int *)(iVar6 + 0x30) == 0) {
    FUN_00440656(iVar6);
  }
  local_20 = *(undefined4 *)(iVar6 + 0x40);
  bVar1 = FUN_00451670(iVar6,0x23,&local_20);
  if (bVar1 == 1) {
    uVar5 = 1;
  }
  else {
    uVar5 = (uint)bVar1;
  }
  return CONCAT44(local_20,uVar5);
}

