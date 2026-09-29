
undefined4 translate_ui_0059e270(undefined4 param_1,int param_2)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_d0;
  undefined *local_cc;
  undefined4 local_b0;
  undefined4 local_a0;
  undefined4 local_70;
  undefined4 local_6c;
  undefined4 local_60;
  undefined4 local_50;
  undefined4 local_40;
  
  iVar1 = DAT_0059e5cc;
  if ((*(int *)(DAT_0059e5cc + 0x10) == 0) || (*(int *)(DAT_0059e5cc + 0x18) == 0)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_cc = (undefined *)DAT_0059e680;
      local_d0 = 0x244;
      FUN_0043d574(2,DAT_0059e640,DAT_0059e63c,DAT_0059e684);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0059e688);
    }
    uVar2 = 0xffffffff;
  }
  else {
    *(undefined1 *)(DAT_0059e5cc + 0x21) = 1;
    FUN_004503d6(&local_70);
    uVar2 = DAT_0059e68c;
    local_70 = *(undefined4 *)(iVar1 + 4);
    local_40 = 300;
    local_50 = DAT_0059e68c;
    local_6c = DAT_0059e690;
    local_60 = DAT_0059e694;
    FUN_004503d6(&local_d0);
    local_d0 = *(undefined4 *)(iVar1 + 0x10);
    local_a0 = 300;
    local_b0 = uVar2;
    local_cc = PTR_translate_ui_0059e248_1_0059e698;
    if (param_2 == 1) {
      *(undefined4 *)(iVar1 + 0x24) = 0;
      FUN_0058c426(*(undefined4 *)(iVar1 + 0x10),300,0);
      FUN_004411aa(*(undefined4 *)(iVar1 + 0x18),0x54,0);
      FUN_004506ce(&local_70,0,0xa6);
      FUN_004506ce(&local_d0,0xfffffff4,0);
    }
    else {
      *(undefined4 *)(iVar1 + 0x24) = 1;
      FUN_0058c238(*(undefined4 *)(iVar1 + 0x10),300,0);
      FUN_004411aa(*(undefined4 *)(iVar1 + 0x18),0x70,0);
      FUN_004506ce(&local_70,0xa6,0);
      FUN_004506ce(&local_d0,0,0xfffffff4);
    }
    FUN_00450408(&local_70);
    FUN_00450408(&local_d0);
    uVar2 = 0;
  }
  return uVar2;
}

