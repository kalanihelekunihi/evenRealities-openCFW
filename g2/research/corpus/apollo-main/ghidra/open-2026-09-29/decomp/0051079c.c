
undefined1 SVC_NvdbInit(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  char cVar2;
  undefined1 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  int local_20;
  undefined1 auStack_1c [8];
  undefined4 uStack_14;
  
  local_20 = 0;
  uStack_14 = param_4;
  if ((param_1 != 0) && (param_2 != 0)) {
    uVar4 = SVC_FlashDBGetObject(1);
    FUN_00545320(uVar4,2,param_1);
    uVar4 = SVC_FlashDBGetObject(1);
    FUN_00545320(uVar4,3,param_2);
  }
  uVar1 = DAT_005109d4;
  uVar4 = DAT_005109d0;
  service_nvdb_defaults_get(auStack_1c);
  uVar5 = SVC_FlashDBGetObject(1);
  cVar2 = FUN_005453fe(uVar5,uVar4,uVar1,auStack_1c,0);
  uVar4 = DAT_005109e4;
  if (cVar2 == '\0') {
    iVar6 = SVC_FlashDBBlobRead(1,DAT_005109e4,&local_20,4);
    iVar7 = FUN_0043d0ce();
    if (iVar7 << 0x1e < 0) {
      FUN_0043d574(3,DAT_005109a8,DAT_005109a4,DAT_005109dc,200,DAT_005109e8,local_20,iVar6);
    }
    iVar7 = FUN_0043d0ce();
    if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
      compress_log_output(0xc800000,DAT_005109ec,DAT_005109ec,local_20,iVar6);
    }
    iVar7 = DAT_005109f0;
    if ((iVar6 == 0) || (local_20 != DAT_005109f0)) {
      if (iVar6 == 0) {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(2,DAT_005109a8,DAT_005109a4,DAT_005109dc,0xcb,DAT_005109f4,0);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x8400000,DAT_005109f8,DAT_005109f8,0);
        }
      }
      else if (local_20 != DAT_005109f0) {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(2,DAT_005109a8,DAT_005109a4,DAT_005109dc,0xcd,DAT_005109fc,local_20,iVar7);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x8800000,DAT_00510a00,DAT_00510a00,local_20,iVar7);
        }
      }
      local_20 = DAT_005109f0;
      SVC_FlashDBGetObject(1);
      FUN_005450a4();
      SVC_FlashDBBlobRead(1,uVar4,&local_20,4);
    }
    service_nvdb_defaults_validate();
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(3,DAT_005109a8,DAT_005109a4,DAT_005109dc,0xda,DAT_00510a04);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_00510a08,DAT_00510a08);
    }
    uVar3 = 0;
  }
  else {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005109a8,DAT_005109a4,DAT_005109dc,0xbf,DAT_005109d8,uVar1,cVar2);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_005109e0,DAT_005109e0,uVar1,cVar2);
    }
    uVar3 = 8;
  }
  return uVar3;
}

