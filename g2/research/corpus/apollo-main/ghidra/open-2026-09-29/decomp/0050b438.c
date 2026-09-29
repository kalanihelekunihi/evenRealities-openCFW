
void FUN_0050b438(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  char cVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 local_8c;
  uint local_88;
  uint local_80;
  uint local_7c;
  uint local_78;
  undefined4 local_74;
  undefined4 local_70;
  undefined1 auStack_64 [12];
  uint local_58;
  uint local_54;
  uint local_50;
  undefined1 auStack_3c [32];
  undefined4 uStack_1c;
  
  puVar1 = DAT_0050b5d4;
  if (((param_1 != 0) && (-1 < (int)param_2)) && ((int)param_2 < *(int *)(DAT_0050bf98 + 0xc0))) {
    uStack_1c = param_4;
    osMutexAcquire(*DAT_0050b5d4,0xffffffff);
    puVar2 = DAT_0050bf9c;
    cVar3 = FUN_0050b19a(DAT_0050bf9c,param_2 & 0xffff);
    osMutexRelease(*puVar1);
    if (cVar3 == '\0') {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_8c = DAT_0050bfa0;
        local_88 = param_2;
        FUN_0043d574(1,DAT_0050b5dc,DAT_0050b5d8,DAT_0050bfa4,0x532);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_0050bfa8,DAT_0050bfa8,param_2);
      }
    }
    else {
      *(undefined4 *)(param_1 + 0x1c) = *puVar2;
      *(undefined1 *)(param_1 + 0x27) = 0;
      *(undefined1 *)(param_1 + 0x28) = 0;
      *(undefined1 *)(param_1 + 0x29) = 1;
      *(undefined4 *)(param_1 + 0x2c) = 0;
      FUN_0049942e(*(undefined4 *)(param_1 + 0xc),puVar2 + 1);
      FUN_0043c0e4(auStack_3c,0x20,0);
      uVar5 = FUN_0047cc60(puVar2[800],puVar2[0x321],1000,0);
      service_time_epoch_to_calendar(uVar5,&local_8c);
      service_time_current_calendar_get(auStack_64);
      if (((local_80 < local_58) || ((local_58 == local_80 && (local_7c < local_54)))) ||
         ((local_58 == local_80 && ((local_54 == local_7c && (local_78 < local_50)))))) {
        FUN_0044b728(auStack_3c,0x20,DAT_0050bfac,local_7c,local_78);
      }
      else {
        FUN_0044b728(auStack_3c,0x20,DAT_0050c1bc,local_74,local_70);
      }
      FUN_0049942e(*(undefined4 *)(param_1 + 0x10),auStack_3c);
      FUN_0043f6d6(*(undefined4 *)(param_1 + 0x10),*(undefined4 *)(param_1 + 4),3,0xfffffff0,0x10);
      FUN_0049942e(*(undefined4 *)(param_1 + 0x14),puVar2 + 0x11);
      FUN_0049942e(*(undefined4 *)(param_1 + 0x18),puVar2 + 0x31);
      FUN_0043f66c(*(undefined4 *)(param_1 + 0x14));
      FUN_0043f6d6(*(undefined4 *)(param_1 + 0x18),*(undefined4 *)(param_1 + 0x14),0xd,0,0xc);
      FUN_0044ea04(*(undefined4 *)(param_1 + 4),0,0);
      FUN_0043f66c(*(undefined4 *)(param_1 + 4));
      FUN_0050b5f4(param_1);
    }
  }
  return;
}

