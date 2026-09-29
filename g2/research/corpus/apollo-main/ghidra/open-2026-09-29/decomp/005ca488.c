
uint FUN_005ca488(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  undefined1 auStack_b4 [8];
  undefined1 auStack_ac [8];
  undefined1 auStack_a4 [48];
  undefined4 local_74;
  undefined1 auStack_64 [48];
  undefined4 local_34;
  undefined4 uStack_24;
  
  uVar5 = *(uint *)(param_1 + 0x48) & 0x7fff;
  uVar2 = param_1;
  if (((1 < uVar5) && (uVar2 = (uint)*(byte *)(param_1 + 0x3c), uVar2 != 0x10)) &&
     (uVar2 = (uint)*(byte *)(param_1 + 0x3c), uVar2 != 8)) {
    uStack_24 = param_4;
    FUN_005c6fbc(auStack_64);
    FUN_00452b0e(param_1,0x20000,auStack_64);
    FUN_005c6fbc(auStack_a4);
    FUN_00452b0e(param_1,0x50000,auStack_a4);
    uVar2 = 0;
    for (uVar6 = 0; uVar6 < uVar5; uVar6 = uVar6 + 1) {
      cVar1 = FUN_005cb402(param_1,uVar6);
      iVar3 = FUN_004888b4(uVar6,0,uVar5 - 1,*(undefined4 *)(param_1 + 0x40),
                           *(undefined4 *)(param_1 + 0x44));
      for (iVar4 = FUN_00482ce4(param_1 + 0x2c); iVar4 != 0;
          iVar4 = FUN_00482cfa(param_1 + 0x2c,iVar4)) {
        if ((*(int *)(iVar4 + 0xc) <= iVar3) && (iVar3 <= *(int *)(iVar4 + 0x10))) {
          if (cVar1 == '\0') {
            FUN_005caede(param_1,auStack_a4,*(undefined4 *)(iVar4 + 8),0x50000);
          }
          else {
            FUN_005caede(param_1,auStack_64,*(undefined4 *)(iVar4 + 4),0x20000);
          }
          break;
        }
        FUN_00452b0e(param_1,0x20000,auStack_64);
        FUN_00452b0e(param_1,0x50000,auStack_a4);
      }
      FUN_005ca9cc(param_1,uVar6,cVar1,auStack_b4,auStack_ac);
      FUN_005cb252(param_1,uVar6,cVar1,local_34,local_74);
      uVar2 = FUN_005cb310(param_1,cVar1,auStack_64,auStack_a4,iVar3,uVar6 & 0xff,auStack_b4);
    }
  }
  return uVar2;
}

