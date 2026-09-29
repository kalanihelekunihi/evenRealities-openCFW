
undefined1 SVC_KvdbInit(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  undefined1 uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  int iVar6;
  undefined4 uVar7;
  int local_28;
  int local_24;
  undefined1 auStack_20 [8];
  undefined4 uStack_18;
  
  local_24 = 0;
  local_28 = 0;
  uStack_18 = param_4;
  iVar3 = FUN_0043d0ce(0);
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004d9ab8,DAT_004d9ab4,DAT_004d9acc,0xa2,DAT_004d9ac8);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_004d9ad0);
  }
  if ((param_1 != 0) && (param_2 != 0)) {
    uVar4 = SVC_FlashDBGetObject(0);
    FUN_00545320(uVar4,2,param_1);
    uVar4 = SVC_FlashDBGetObject(0);
    FUN_00545320(uVar4,3,param_2);
  }
  uVar7 = DAT_004d9ad4;
  uVar4 = DAT_004d9ab8;
  SVC_KvdbDefaultDescriptor(auStack_20);
  uVar5 = SVC_FlashDBGetObject(0);
  cVar1 = FUN_005453fe(uVar5,uVar7,uVar4,auStack_20,0);
  uVar7 = DAT_004d9ae0;
  if (cVar1 == '\0') {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,uVar4,DAT_004d9ab4,DAT_004d9acc,0xb4,DAT_004d9ae4,uVar7);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004d9ae8,DAT_004d9ae8,uVar7);
    }
    iVar3 = SVC_FlashDBBlobRead(0,uVar7,&local_28,4);
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(4,uVar4,DAT_004d9ab4,DAT_004d9acc,0xb7,DAT_004d9aec,local_28,iVar3);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_004d9af0,DAT_004d9af0,local_28,iVar3);
    }
    iVar6 = DAT_004d9af4;
    if ((iVar3 == 0) || (local_28 != DAT_004d9af4)) {
      if (iVar3 == 0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(2,uVar4,DAT_004d9ab4,DAT_004d9acc,0xba,DAT_004d9af8,0);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x8400000,DAT_004d9afc,DAT_004d9afc,0);
        }
      }
      else if (local_28 != DAT_004d9af4) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(2,uVar4,DAT_004d9ab4,DAT_004d9acc,0xbc,DAT_004d9b00,local_28,iVar6);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x8800000,DAT_004d9b04,DAT_004d9b04,local_28,iVar6);
        }
        SVC_KvdbReadOnboardingConfig(1);
      }
      local_28 = DAT_004d9af4;
      SVC_FlashDBGetObject(0);
      FUN_005450a4();
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,uVar4,DAT_004d9ab4,DAT_004d9acc,0xc2,DAT_004d9b08);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004d9b0c,DAT_004d9b0c);
      }
      SVC_KvdbBlobWriteOnboardingConfig();
      uVar7 = SVC_FlashDBBlobRead(0,uVar7,&local_28,4);
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,uVar4,DAT_004d9ab4,DAT_004d9acc,0xc5,DAT_004d9b10,local_28,uVar7);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_004d9b14,DAT_004d9b14,local_28,uVar7);
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,uVar4,DAT_004d9ab4,DAT_004d9acc,199,DAT_004d9b18,local_28);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004d9b1c,DAT_004d9b1c,local_28);
      }
    }
    uVar7 = DAT_004d9b20;
    SVC_FlashDBBlobRead(0,DAT_004d9b20,&local_24,4);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(3,uVar4,DAT_004d9ab4,DAT_004d9acc,0xcc,DAT_004d9b24,local_24);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_004d9b28,DAT_004d9b28,local_24);
    }
    local_24 = local_24 + 1;
    SVC_FlashDBBlobWrite(0,uVar7,&local_24,4);
    SVC_KvdbRunMigrations();
    SVC_KvdbReadAll();
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(3,uVar4,DAT_004d9ab4,DAT_004d9acc,0xd4,DAT_004d9b2c);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_004d9b30,DAT_004d9b30);
    }
    uVar2 = 0;
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,uVar4,DAT_004d9ab4,DAT_004d9acc,0xae,DAT_004d9ad8,uVar4,cVar1);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_004d9adc,DAT_004d9adc,uVar4,cVar1);
    }
    uVar2 = 8;
  }
  return uVar2;
}

