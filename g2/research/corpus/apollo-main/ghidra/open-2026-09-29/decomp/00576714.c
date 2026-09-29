
void pt_cmd_60_handler(int param_1,byte param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  int iVar2;
  uint uVar3;
  
  if (param_2 < 0xfa) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005768bc,DAT_005768b8,DAT_005771b8,0xd38,DAT_005771b4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005771bc,DAT_005771bc);
    }
    pt_handler_result(0xf3,1,2,param_3,param_4);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_005768bc,DAT_005768b8,DAT_005771b8,0xd3c,DAT_005771c0);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_0057746c,DAT_0057746c);
    }
    bVar1 = true;
    for (uVar3 = 0; (int)uVar3 < 0xf6; uVar3 = uVar3 + 1) {
      if (*(byte *)(param_1 + uVar3 + 4) != uVar3) {
        bVar1 = false;
        break;
      }
    }
    if (bVar1) {
      pt_handler_result(0xf3,0,2,param_3,param_4);
    }
    else {
      pt_handler_result(0xf3,1,2,param_3,param_4);
    }
  }
  return;
}

