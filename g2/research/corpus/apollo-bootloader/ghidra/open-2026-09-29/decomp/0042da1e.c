
int chunked_source_compare_42da1e(int param_1,int param_2,uint param_3,int param_4)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  
  iVar4 = 0;
  FUN_0041e348(0,1);
  uVar3 = param_3;
  while( true ) {
    uVar1 = DAT_0042e11c;
    if (uVar3 == 0) {
      return 0;
    }
    uVar5 = uVar3;
    if (0x1000 < uVar3) {
      uVar5 = 0x1000;
    }
    (**(code **)(param_4 + 0x18))(DAT_0042e11c,iVar4 + param_1,uVar5);
    iVar2 = FUN_00415758(uVar1,iVar4 + param_2,uVar5);
    if (iVar2 != 0) break;
    elog_output(4,DAT_0042e118,DAT_0042e114,DAT_0042e138,0x10e,DAT_0042e134,param_1,param_3,uVar3);
    iVar4 = uVar5 + iVar4;
    uVar3 = uVar3 - uVar5;
  }
  elog_output(1,DAT_0042e118,DAT_0042e114,DAT_0042e138,0x10b,DAT_0042e13c,param_1,param_3);
  return iVar2;
}

