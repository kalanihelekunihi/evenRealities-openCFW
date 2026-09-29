
void FUN_005b8f18(uint param_1,char param_2)

{
  int iVar1;
  int *piVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined1 auStack_34 [16];
  
  piVar2 = DAT_005b9b00;
  iVar1 = DAT_005b9a64;
  if ((param_1 < 3) && (*DAT_005b9b00 != 0)) {
    *(char *)(param_1 * 0xc + DAT_005b9a64 + 8) = param_2;
    *(undefined1 *)(param_1 * 0xc + iVar1 + 9) = 1;
    *(undefined4 *)(iVar1 + param_1 * 0xc) = 0;
    *(undefined4 *)(param_1 * 0xc + iVar1 + 4) = 0;
    if (param_2 != '\0') {
      uVar3 = FUN_0043de82(*piVar2);
      FUN_0043f4c0(uVar3,0x3fffffff,0x3fffffff);
      FUN_0044129e(uVar3,0,0);
      FUN_0044131c(uVar3,0,0);
      FUN_0044133a(uVar3,0,0);
      FUN_00441386(uVar3,0,0);
      FUN_005b8dd0(uVar3,0,0);
      FUN_0044146a(uVar3,0,0);
      uVar4 = FUN_0044104c(0xffffff);
      FUN_0044140e(uVar3,uVar4,0);
      FUN_0044142e(uVar3,0xff,0);
      FUN_0043dfa4(uVar3,0x10);
      *(undefined4 *)(DAT_005b9c44 + param_1 * 4) = uVar3;
      uVar4 = FUN_00498668(uVar3);
      FUN_0043f506(uVar4,0x18);
      FUN_0043f568(uVar4,0x18);
      FUN_0043f09a(uVar4,0,0);
      FUN_0043ded4(uVar4,0x10000);
      FUN_0043dfa4(uVar4,0x10);
      *(undefined4 *)(iVar1 + param_1 * 0xc) = uVar4;
      FUN_005b8d20(param_1 * 0xc + iVar1);
      uVar5 = FUN_00499416(uVar3);
      FUN_0043f506(uVar5,0x3fffffff);
      FUN_0043f568(uVar5,0x3fffffff);
      FUN_0044143e(uVar5,*DAT_005b9c48,0);
      *(undefined4 *)(iVar1 + param_1 * 0xc + 4) = uVar5;
      FUN_0043c0e4(auStack_34,0x10,0);
      FUN_005b8bc8(param_2,auStack_34,0x10);
      FUN_0049942e(uVar5,auStack_34);
      FUN_0043f6d6(uVar5,uVar4,0x14,8,0);
      FUN_005b8e5e(param_1,*DAT_005b9c60);
      uVar4 = FUN_005b8e4a();
      FUN_005b8e1a(uVar3,uVar4);
    }
  }
  return;
}

