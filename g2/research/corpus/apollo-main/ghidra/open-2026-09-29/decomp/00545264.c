
undefined4
FUN_00545264(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  uint local_84;
  undefined1 auStack_80 [24];
  undefined1 auStack_68 [88];
  undefined4 uStack_10;
  
  local_84 = 0;
  *(undefined1 *)((int)param_1 + 0x31) = 1;
  uStack_10 = param_4;
  FUN_00544736(param_1,auStack_80,0,&local_84,param_1,DAT_0054555c,0);
  if ((*(char *)((int)param_1 + 0x1a) == '\0') || (local_84 == 0)) {
    if (local_84 == (uint)param_1[4] / (uint)param_1[3]) {
      FUN_004733ee(DAT_00545534);
      uVar1 = FUN_00585c94(param_1);
      FUN_004733ee(DAT_00545538,*param_1,uVar1);
      FUN_004733ee(DAT_00545560);
      FUN_005450a4(param_1);
    }
    FUN_00544736(param_1,auStack_80,0,param_1,0,DAT_00545564,0);
    while( true ) {
      FUN_005443b0(param_1,auStack_68,param_1,0,DAT_00545568);
      if (*(char *)(param_1 + 0xc) == '\0') break;
      FUN_00544cec(param_1);
    }
    *(undefined1 *)((int)param_1 + 0x31) = 0;
    uVar1 = 0;
  }
  else {
    uVar1 = 2;
  }
  return uVar1;
}

