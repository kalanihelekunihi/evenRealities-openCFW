
undefined8 FUN_005cb1a8(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  uint uVar6;
  uint uVar7;
  undefined4 local_28;
  
  uVar4 = *(undefined4 *)(param_1 + 0x40);
  uVar5 = *(undefined4 *)(param_1 + 0x44);
  uVar6 = *(uint *)(param_1 + 0x48) & 0x7fff;
  local_28 = param_3;
  for (uVar7 = 0; uVar7 < uVar6; uVar7 = uVar7 + 1) {
    uVar1 = FUN_005cb402(param_1,uVar7);
    iVar2 = FUN_004888b4(uVar7,0,uVar6 - 1,uVar4);
    iVar3 = FUN_00482ce4(param_1 + 0x2c);
    while (iVar3 != 0) {
      if ((*(int *)(iVar3 + 0xc) <= iVar2) && (iVar2 <= *(int *)(iVar3 + 0x10))) {
        if (*(int *)(iVar3 + 0x14) == 0xff) {
          *(uint *)(iVar3 + 0x14) = uVar7;
          *(uint *)(iVar3 + 0x34) = *(uint *)(iVar3 + 0x34) & 0xfffffffe | uVar1 & 1;
        }
        if (*(int *)(iVar3 + 0x18) == 0xff) {
          *(uint *)(iVar3 + 0x18) = uVar7;
          *(uint *)(iVar3 + 0x34) = *(uint *)(iVar3 + 0x34) & 0xfffffffd | (uVar1 & 1) << 1;
        }
        else if (*(uint *)(iVar3 + 0x14) != uVar7) {
          *(uint *)(iVar3 + 0x18) = uVar7;
          *(uint *)(iVar3 + 0x34) = *(uint *)(iVar3 + 0x34) & 0xfffffffd | (uVar1 & 1) << 1;
        }
      }
      iVar3 = FUN_00482cfa(param_1 + 0x2c);
    }
    local_28 = uVar5;
  }
  return CONCAT44(param_4,local_28);
}

