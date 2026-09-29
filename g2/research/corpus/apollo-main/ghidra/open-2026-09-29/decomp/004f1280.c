
undefined4 FUN_004f1280(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  if (param_1 != 0) {
    iVar3 = *DAT_004f1a48;
    iVar1 = *DAT_004f1a48;
    iVar4 = *DAT_004f1a4c;
    iVar2 = *DAT_004f1a4c;
    FUN_0043f09a(param_1,(param_2 * *DAT_004f1a3c) / DAT_004f1a40 + *DAT_004f1a3c,
                 (param_2 * *DAT_004f1a44) / DAT_004f1a40 + *DAT_004f1a44);
    FUN_0043f4c0(param_1,(param_2 * (0x240 - iVar1)) / 1000 + iVar3,
                 (param_2 * (0x120 - iVar2)) / 1000 + iVar4);
  }
  return param_4;
}

