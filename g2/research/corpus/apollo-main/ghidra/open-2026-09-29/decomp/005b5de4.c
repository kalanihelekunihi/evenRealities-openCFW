
undefined8
conversate_tag_extend_page_input_event_handler
          (int param_1,int param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  
  iVar1 = DAT_005b6958;
  iVar4 = param_2;
  if (*(int *)(DAT_005b6958 + 0x1c) != 0) {
    if (*(char *)(DAT_005b6958 + 0x98) == '\0') {
      FUN_005b3c2a();
      uVar2 = FUN_0044dce2(*(undefined4 *)(iVar1 + 0x1c),1);
      if (param_1 == 10) {
        if (*(char *)(iVar1 + 0xa4) == '\x01') {
          FUN_005b02e4(10,0);
        }
      }
      else if (param_1 == 0x48) {
        FUN_005b02e4(10,1);
      }
      else if (param_1 == 0x44) {
        iVar1 = FUN_005546be(uVar2,-(*(undefined4 **)(param_2 + 0x10))[1],
                             **(undefined4 **)(param_2 + 0x10),0x1c);
        iVar3 = FUN_0044e498(uVar2);
        if (iVar1 != iVar3) {
          FUN_005b02e4(0xe,iVar1);
        }
      }
      else if (param_1 == 0x45) {
        iVar1 = FUN_005546be(uVar2,(*(undefined4 **)(param_2 + 0x10))[1],
                             **(undefined4 **)(param_2 + 0x10),0x1c);
        iVar3 = FUN_0044e498(uVar2);
        if (iVar1 != iVar3) {
          FUN_005b02e4(0xf,iVar1);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      iVar4 = param_2;
      if (iVar1 << 0x1e < 0) {
        iVar4 = 0x31;
        param_3 = DAT_005b695c;
        param_4 = param_1;
        FUN_0043d574(3,DAT_005b6950,DAT_005b694c,DAT_005b6960,0x31,DAT_005b695c,param_1);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_005b6964,DAT_005b6964,param_1,iVar4,param_3,param_4);
      }
    }
  }
  return CONCAT44(param_3,iVar4);
}

