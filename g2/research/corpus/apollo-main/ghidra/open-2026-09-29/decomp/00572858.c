
undefined4 pt_cmd_25_handler(int param_1,uint param_2,undefined1 *param_3,char *param_4)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (char *)0x0)) || (param_1 == 0)) ||
     ((param_2 & 0xff) < 4)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_1 = 0x7c8;
      param_2 = DAT_00573200;
      param_3 = DAT_005734c8;
      FUN_0043d574(1,DAT_00572ae8,DAT_00572ae4,DAT_005734c8,0x7c8,DAT_00573200,DAT_005734c8,param_4)
      ;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00573300,DAT_00573300,DAT_005734c8,param_1,param_2,param_3);
    }
    uVar3 = 0xffffffff;
  }
  else {
    uVar3 = SVC_NvdbGetSysData(1);
    *param_3 = 0x2a;
    param_3[1] = 1;
    param_3[2] = 3;
    uVar4 = FUN_0044a43c(uVar3);
    if (uVar4 < 0x16) {
      cVar1 = FUN_0044a43c(uVar3);
    }
    else {
      cVar1 = '\x15';
    }
    param_3[3] = cVar1;
    FUN_00439be4(param_3 + 4,uVar3,cVar1);
    *param_4 = cVar1 + '\x04';
    uVar3 = 0;
  }
  return uVar3;
}

