
undefined4 FUN_005001d2(uint param_1,int param_2,undefined4 param_3,undefined4 param_4,char param_5)

{
  undefined1 *puVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  uint uVar6;
  
  puVar1 = DAT_00500308;
  *DAT_00500308 = 5;
  *(uint *)(puVar1 + 4) = param_1;
  *(undefined4 *)(puVar1 + 0x30) = param_3;
  *(undefined4 *)(puVar1 + 0x34) = param_4;
  puVar1[0x38] = param_5;
  uVar6 = param_1;
  if (10 < param_1) {
    uVar6 = 10;
  }
  uVar5 = param_4;
  if ((uVar6 == 0) || (param_2 == 0)) {
    FUN_0043c0e4(puVar1 + 8,0x28,0);
  }
  else {
    FUN_00439be4(puVar1 + 8,param_2,uVar6 << 2);
  }
  uVar2 = FUN_004ffef8(puVar1);
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    uVar4 = DAT_0050035c;
    if (param_5 != '\0') {
      uVar4 = DAT_00500358;
    }
    FUN_0043d574(4,DAT_00500300,DAT_005002fc,DAT_00500364,0x100,DAT_00500360,param_1,param_3,param_4
                 ,uVar4,uVar5);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    uVar5 = DAT_0050035c;
    if (param_5 != '\0') {
      uVar5 = DAT_00500358;
    }
    compress_log_output(0x11000000,DAT_00500368,DAT_00500368,param_1,param_3,param_4,uVar5);
  }
  return uVar2;
}

