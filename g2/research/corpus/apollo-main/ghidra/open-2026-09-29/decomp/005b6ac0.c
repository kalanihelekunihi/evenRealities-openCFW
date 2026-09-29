
void FUN_005b6ac0(short param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  ushort uVar2;
  int iVar3;
  ushort uVar4;
  ushort uVar5;
  undefined1 auStack_a8 [132];
  undefined4 uStack_24;
  
  iVar1 = DAT_005b7604;
  uStack_24 = param_4;
  uVar2 = FUN_005b4770();
  for (uVar4 = 0; uVar4 < 0xc; uVar4 = uVar4 + 1) {
    uVar5 = uVar4 + param_1;
    iVar3 = *(int *)(iVar1 + (uint)uVar4 * 4 + 0x30);
    if (iVar3 != 0) {
      FUN_0043f09a(iVar3,0,(uint)uVar5 * 0x1c);
      if (uVar5 < uVar2) {
        FUN_0043c0e4(auStack_a8,0x81,0);
        FUN_005b4776(uVar5,auStack_a8,0x81);
        FUN_0049942e(iVar3,auStack_a8);
        FUN_0043dfa4(iVar3,1);
      }
      else {
        FUN_0049942e(iVar3,&DAT_005b6ccc);
        FUN_0043ded4(iVar3,1);
      }
    }
  }
  *(short *)(iVar1 + 0x60) = param_1;
  return;
}

