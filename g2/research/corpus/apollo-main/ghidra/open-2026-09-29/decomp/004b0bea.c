
uint FUN_004b0bea(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  undefined4 local_28;
  undefined4 uStack_24;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 uStack_18;
  
  uStack_18 = param_4;
  iVar2 = FUN_004c791a();
  FUN_00514e50(*(undefined4 *)(iVar2 + 0x44));
  FUN_00515048(*(undefined4 *)(iVar2 + 0x48));
  FUN_00515676();
  FUN_004b075e(iVar2);
  uVar3 = param_1 + 3U & 0xfffffffc;
  uVar4 = param_2 + 3U & 0xfffffffc;
  bVar1 = FUN_004b0b5a(iVar2,uVar3,uVar4);
  if (bVar1 == 1) {
    FUN_0048949c(&local_28,0x10);
    local_28 = *(undefined4 *)(*(int *)(iVar2 + 0x40) + 0xc);
    local_20 = *(undefined4 *)(*(int *)(iVar2 + 0x40) + 0x10);
    local_1c = *(undefined4 *)(*(int *)(iVar2 + 0x40) + 0x10);
    uVar3 = FUN_005223a2(uVar3,uVar4,local_28,uStack_24,local_20,local_1c);
  }
  else {
    FUN_0044d25c(3,DAT_004b1054,0x1fd,DAT_004b1090,DAT_004b108c);
    uVar3 = (uint)bVar1;
  }
  return uVar3;
}

