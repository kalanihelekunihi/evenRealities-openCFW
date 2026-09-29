
undefined4 FUN_0045360c(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  undefined4 local_10;
  
  if (param_1 == 0) {
    uVar2 = FUN_0044fa1a();
    *(undefined4 *)(DAT_00454168 + 0x10) = uVar2;
  }
  else {
    *(undefined4 *)(DAT_00454168 + 0x10) = *(undefined4 *)(param_1 + 0xc);
    FUN_0046450c();
  }
  iVar1 = DAT_00454168;
  if (*(int *)(DAT_00454168 + 0x10) == 0) {
    local_10 = DAT_0045416c;
    FUN_0044d25c(2,DAT_00454164,0x174,DAT_00454170);
  }
  else {
    iVar3 = *(int *)(*(int *)(DAT_00454168 + 0x10) + 0x24);
    if (((iVar3 == 0) || (*(int *)(iVar3 + 0x10) == 0)) || (*(int *)(iVar3 + 0xc) == 0)) {
      local_10 = DAT_00454174;
      FUN_0044d25c(2,DAT_00454164,0x17b,DAT_00454170);
    }
    else {
      FUN_0044fdbe(*(undefined4 *)(DAT_00454168 + 0x10),0x39,0);
      FUN_0043f66c(*(undefined4 *)(*(int *)(iVar1 + 0x10) + 0x2c4));
      if (*(int *)(*(int *)(iVar1 + 0x10) + 0x2cc) != 0) {
        FUN_0043f66c(*(undefined4 *)(*(int *)(iVar1 + 0x10) + 0x2cc));
      }
      FUN_0043f66c(*(undefined4 *)(*(int *)(iVar1 + 0x10) + 0x2c8));
      FUN_0043f66c(*(undefined4 *)(*(int *)(iVar1 + 0x10) + 0x2c0));
      FUN_0043f66c(*(undefined4 *)(*(int *)(iVar1 + 0x10) + 700));
      if (*(int *)(*(int *)(iVar1 + 0x10) + 0x2c4) == 0) {
        *(undefined4 *)(*(int *)(iVar1 + 0x10) + 0x260) = 0;
        local_10 = DAT_00454178;
        FUN_0044d25c(2,DAT_00454164,399,DAT_00454170);
      }
      else {
        FUN_0045377a();
        FUN_0045383c();
        FUN_004539b6();
        local_10 = param_4;
        if (*(int *)(*(int *)(iVar1 + 0x10) + 0x260) != 0) {
          iVar3 = FUN_0044fc52(*(undefined4 *)(iVar1 + 0x10));
          if ((iVar3 != 0) && (*(char *)(*(int *)(iVar1 + 0x10) + 0x39) == '\x01')) {
            for (uVar4 = 0; uVar4 < *(uint *)(*(int *)(iVar1 + 0x10) + 0x260); uVar4 = uVar4 + 1) {
              if (*(char *)(*(int *)(iVar1 + 0x10) + uVar4 + 0x240) == '\0') {
                uVar2 = FUN_00482bca(*(int *)(iVar1 + 0x10) + 0x268);
                FUN_00439c04(uVar2,*(int *)(iVar1 + 0x10) + uVar4 * 0x10 + 0x40,0x10);
              }
            }
          }
          FUN_0045310e(*(int *)(iVar1 + 0x10) + 0x40,0x200);
          FUN_0045310e(*(int *)(iVar1 + 0x10) + 0x240,0x20);
          *(undefined4 *)(*(int *)(iVar1 + 0x10) + 0x260) = 0;
        }
      }
      FUN_0044fdbe(*(undefined4 *)(iVar1 + 0x10),0x3a,0);
    }
  }
  return local_10;
}

