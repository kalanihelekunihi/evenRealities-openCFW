
undefined4 FUN_00589d74(char *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  byte bVar2;
  int iVar3;
  undefined4 uVar4;
  
  cVar1 = *param_1;
  if (cVar1 == '\x01') {
    bVar2 = param_1[4];
    if (bVar2 == 1) {
      uVar4 = FUN_0058c89e(1,param_1 + 4,0x30,param_4,param_1,param_2,param_3,param_4);
    }
    else {
      if (bVar2 != 0) {
        if (bVar2 == 3) {
          uVar4 = FUN_0058c89e(3,param_1 + 4,0x30,param_4,param_1,param_2,param_3,param_4);
          return uVar4;
        }
        if (bVar2 < 3) {
          uVar4 = FUN_0058c89e(2,param_1 + 4,0x30,param_4,param_1,param_2,param_3,param_4);
          return uVar4;
        }
        if (bVar2 == 4) {
          uVar4 = FUN_0058c89e(4,param_1 + 4,0x30,param_4,param_1,param_2,param_3,param_4);
          return uVar4;
        }
      }
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0058a320,DAT_0058a31c,DAT_0058a384,0xcd,DAT_0058a380,param_1[4]);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_0058a388,DAT_0058a388,param_1[4]);
      }
      uVar4 = 0xffffffff;
    }
  }
  else if (cVar1 == '\x02') {
    uVar4 = FUN_0058c89e(5,param_1 + 4,0xf52,param_4,param_1,param_2,param_3,param_4);
  }
  else if (cVar1 == '\x03') {
    uVar4 = FUN_0058c89e(6,param_1 + 4,0x40c,param_4,param_1,param_2,param_3,param_4);
  }
  else if (cVar1 == '\x04') {
    uVar4 = FUN_0058c89e(7,param_1 + 4,0xc,param_4,param_1,param_2,param_3,param_4);
  }
  else if (cVar1 == -0x5b) {
    uVar4 = FUN_0058c89e(8,param_1 + 4,0xc,param_4,param_1,param_2,param_3,param_4);
  }
  else if (cVar1 == -1) {
    uVar4 = FUN_0058c89e(9,param_1 + 4,0x10,param_4,param_1,param_2,param_3,param_4);
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0058a320,DAT_0058a31c,DAT_0058a384,0xdb,DAT_0058a38c,*param_1);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8400000,PTR_s__teleprompt_unknown_command_id___0058a390,
                          PTR_s__teleprompt_unknown_command_id___0058a390,*param_1);
    }
    uVar4 = 0xffffffff;
  }
  return uVar4;
}

