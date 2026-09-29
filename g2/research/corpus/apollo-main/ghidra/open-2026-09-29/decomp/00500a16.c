
undefined8 FUN_00500a16(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0xc5;
    param_3 = DAT_005011ac;
    param_4 = param_1;
    FUN_0043d574(3,DAT_00501188,DAT_00501184,DAT_005011b0,0xc5,DAT_005011ac,param_1);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__dashboard_ext_STEP1__handle_APP_005011b4,
                        PTR_s__dashboard_ext_STEP1__handle_APP_005011b4,param_1,param_2,param_3,
                        param_4);
  }
  puVar1 = DAT_00501170;
  FUN_0043c0e4(DAT_00501170,0x1024,0);
  *puVar1 = 1;
  *(undefined4 *)(puVar1 + 4) = param_1;
  *(undefined2 *)(puVar1 + 8) = 4;
  iVar2 = FUN_0055876a();
  *(uint *)(puVar1 + 0xc) = (uint)(iVar2 != 0);
  if (*(int *)(puVar1 + 0xc) == 1) {
    uVar3 = FUN_005020f0();
    uVar4 = FUN_00502108();
    FUN_0044b5a0(puVar1 + 0x10,uVar3,0xf);
    puVar1[0x1f] = 0;
    FUN_0044b5a0(puVar1 + 0x20,uVar4,0x1f);
    puVar1[0x3f] = 0;
  }
  FUN_00500a02();
  return CONCAT44(param_3,param_2);
}

