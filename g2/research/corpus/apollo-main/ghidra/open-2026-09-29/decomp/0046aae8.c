
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
system_close_create_options(int param_1,undefined *param_2,int param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  int *piVar3;
  undefined *puVar4;
  undefined4 *puVar5;
  int iVar6;
  undefined4 uVar7;
  int iVar8;
  
  iVar8 = param_1;
  iVar6 = FUN_0043d0ce();
  if (iVar6 << 0x1e < 0) {
    iVar8 = 0x220;
    param_2 = PTR_s_system_close_create_options__sty_0046b078;
    param_3 = param_1;
    FUN_0043d574(4,DAT_0046b058,DAT_0046b054,PTR_s_system_close_create_options_0046b07c,0x220,
                 PTR_s_system_close_create_options__sty_0046b078,param_1,param_4);
  }
  iVar6 = FUN_0043d0ce();
  if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__system_close_system_close_creat_0046b080,
                        PTR_s__system_close_system_close_creat_0046b080,param_1,iVar8,param_2,
                        param_3);
  }
  if (param_1 == 1) {
    *DAT_0046b00c = 2;
  }
  else {
    *DAT_0046b00c = 3;
  }
  puVar2 = DAT_0046ae94;
  puVar1 = _DAT_0046accc;
  uVar7 = FUN_00498668(*_DAT_0046accc);
  *puVar2 = uVar7;
  FUN_00498680(*puVar2,PTR_DAT_0046b084);
  FUN_0043f4c0(*puVar2,0x12,0x12);
  puVar2 = DAT_0046acd4;
  if (param_1 == 1) {
    uVar7 = FUN_00499416(*puVar1);
    *puVar2 = uVar7;
    puVar4 = PTR_s_ID_GENERAL_NO_0046b088;
    uVar7 = FUN_00460084(PTR_s_ID_GENERAL_NO_0046b088);
    uVar7 = FUN_0045fffe(puVar4,uVar7);
    FUN_0049942e(*puVar2,uVar7);
    puVar5 = _DAT_0046b08c;
    FUN_0044143e(*puVar2,*_DAT_0046b08c,0);
    FUN_0043f506(*puVar2,0x3fffffff);
    FUN_0043f568(*puVar2,0x3fffffff);
    FUN_0043ded4(*puVar2,0x10000);
    FUN_0043dfa4(*puVar2,0x10);
    uVar7 = FUN_0044104c(0xffffff);
    FUN_0044140e(*puVar2,uVar7,0);
    puVar2 = DAT_0046acd8;
    uVar7 = FUN_00499416(*puVar1);
    *puVar2 = uVar7;
    puVar4 = PTR_s_ID_GENERAL_YES_0046b090;
    uVar7 = FUN_00460084(PTR_s_ID_GENERAL_YES_0046b090);
    uVar7 = FUN_0045fffe(puVar4,uVar7);
    FUN_0049942e(*puVar2,uVar7);
    FUN_0044143e(*puVar2,*puVar5,0);
    FUN_0043f506(*puVar2,0x3fffffff);
    FUN_0043f568(*puVar2,0x3fffffff);
    FUN_0043ded4(*puVar2,0x10000);
    FUN_0043dfa4(*puVar2,0x10);
    uVar7 = FUN_0044104c(0xffffff);
    FUN_0044140e(*puVar2,uVar7,0);
  }
  piVar3 = DAT_0046ae98;
  *DAT_0046ae98 = 0;
  iVar6 = FUN_0043d0ce();
  if (iVar6 << 0x1e < 0) {
    iVar8 = 0x25b;
    param_2 = PTR_s_Options_created__item_count__d__s_0046b094;
    FUN_0043d574(4,DAT_0046b058,DAT_0046b054,PTR_s_system_close_create_options_0046b07c,0x25b,
                 PTR_s_Options_created__item_count__d__s_0046b094,*DAT_0046b00c,*piVar3);
  }
  iVar6 = FUN_0043d0ce();
  if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
    iVar8 = *piVar3;
    compress_log_output(0x10800000,PTR_s__system_close_Options_created__i_0046b098,
                        PTR_s__system_close_Options_created__i_0046b098,*DAT_0046b00c);
  }
  return CONCAT44(param_2,iVar8);
}

