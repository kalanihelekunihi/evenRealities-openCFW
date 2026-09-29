
undefined8 FUN_00492cee(undefined4 param_1,undefined4 param_2,int param_3,undefined4 *param_4)

{
  int *piVar1;
  int *piVar2;
  char cVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 *puVar6;
  
  if (param_3 == 0x42) {
    *DAT_00493504 = 1;
    puVar6 = (undefined4 *)0x0;
    if (param_4 != (undefined4 *)0x0) {
      puVar6 = (undefined4 *)*param_4;
    }
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      param_2 = 0x58;
      param_3 = DAT_00493508;
      param_4 = puVar6;
      FUN_0043d574(3,DAT_00493514,DAT_00493510,DAT_0049350c,0x58,DAT_00493508,puVar6);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_00493518,DAT_00493518,puVar6,param_2,param_3,param_4);
    }
    piVar1 = DAT_0049351c;
    if (((*DAT_0049351c != 0) && (puVar6 != (undefined4 *)0x0)) && (puVar6 != (undefined4 *)0x21)) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        param_2 = 0x5a;
        FUN_0043d574(4,DAT_00493514,DAT_00493510,DAT_0049350c,0x5a,DAT_00493520);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_00493524,DAT_00493524);
      }
      FUN_00441488(*piVar1,0x7f,0);
      *DAT_00493528 = 1;
    }
  }
  else if (param_3 == 0x43) {
    *DAT_00493504 = 0;
    piVar2 = DAT_00493528;
    piVar1 = DAT_0049351c;
    if ((*DAT_0049351c != 0) && (*DAT_00493528 == 1)) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        param_2 = 99;
        FUN_0043d574(4,DAT_00493514,DAT_00493510,DAT_0049350c,99,DAT_0049352c);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_00493530,DAT_00493530);
      }
      FUN_00441488(*piVar1,0xff,0);
      *piVar2 = 0;
    }
  }
  else if (((param_3 != 10) && (param_3 != 0x44)) && (param_3 != 0x45)) {
    if (param_3 == 0x48) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        param_2 = 0x74;
        FUN_0043d574(3,DAT_00493514,DAT_00493510,DAT_0049350c,0x74,DAT_00493534);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_00493538,DAT_00493538);
      }
      iVar4 = FUN_0045a568();
      if (iVar4 == 1) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          param_2 = 0x76;
          FUN_0043d574(3,DAT_00493514,DAT_00493510,DAT_0049350c,0x76,DAT_0049353c);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_00493540,DAT_00493540);
        }
        system_close_page_factory_0046ae9c(1,0xffe);
      }
    }
    else if (param_3 == 0x4f) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        param_2 = 0x7b;
        FUN_0043d574(4,DAT_00493514,DAT_00493510,DAT_0049350c,0x7b,DAT_00493544);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_00493548,DAT_00493548);
      }
      cVar3 = FUN_0045a570();
      if (cVar3 == '\x01') {
        uVar5 = FUN_00464c36(0xffe,0,0,0);
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          param_2 = 0x7f;
          FUN_0043d574(4,DAT_00493514,DAT_00493510,DAT_0049350c,0x7f,DAT_0049354c,uVar5);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x10400000,PTR_s__evenhub_loading_page_systemClos_00493550,
                              PTR_s__evenhub_loading_page_systemClos_00493550,uVar5);
        }
      }
    }
  }
  return CONCAT44(param_2,1);
}

