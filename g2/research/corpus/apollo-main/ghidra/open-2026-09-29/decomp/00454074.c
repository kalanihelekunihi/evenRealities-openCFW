
undefined4
FUN_00454074(int param_1,undefined4 param_2,char param_3,undefined4 param_4,undefined4 param_5)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 local_60 [4];
  undefined1 auStack_50 [16];
  undefined1 auStack_40 [16];
  undefined1 auStack_30 [16];
  undefined4 uStack_20;
  
  uStack_20 = param_4;
  uVar1 = FUN_00452dc8(param_2);
  FUN_0043fc2a(param_2,param_5);
  FUN_00450b98(param_5,uVar1,uVar1);
  if (param_3 == '\x02') {
    FUN_00439c04(auStack_50,param_5,0x10);
    FUN_00440494(param_2,auStack_50,0);
    iVar2 = FUN_00450bcc(auStack_30,param_1 + 0x18,auStack_50);
    if (iVar2 == 0) {
      return 0;
    }
    FUN_00439c04(local_60,auStack_30,0x10);
    FUN_00440494(param_2,local_60,2);
    iVar2 = FUN_00450bcc(local_60,local_60,param_5);
    if (iVar2 == 0) {
      return 0;
    }
    FUN_00439c04(param_4,local_60,0x10);
    FUN_00450b98(param_4,5,5);
  }
  else {
    if (param_3 != '\x01') {
      local_60[0] = DAT_0045462c;
      FUN_0044d25c(2,DAT_00454164,0x3c1,DAT_00454630);
      return 0;
    }
    iVar2 = FUN_00450bcc(auStack_40,param_1 + 0x18,param_5);
    if (iVar2 == 0) {
      return 0;
    }
    FUN_00439c04(param_4,auStack_40,0x10);
  }
  return 1;
}

