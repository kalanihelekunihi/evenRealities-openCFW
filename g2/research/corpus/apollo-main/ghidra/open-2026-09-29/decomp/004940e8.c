
undefined4 FUN_004940e8(int param_1)

{
  byte bVar1;
  undefined *puVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 *puVar5;
  undefined4 uVar6;
  
  puVar2 = PTR_s_IMAGE_00494b50;
  uVar6 = DAT_00494b4c;
  uVar3 = DAT_00494b3c;
  if (param_1 == 0) {
    uVar3 = 0xffffffff;
  }
  else {
    bVar1 = *(byte *)(param_1 + 8);
    if (bVar1 == 0) {
      puVar5 = *(undefined4 **)(param_1 + 0xc);
      uVar6 = puVar5[8];
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00494480,DAT_0049447c,DAT_00494b44,0x233,DAT_00494b40,uVar3,uVar6,
                     puVar5 + 9,*puVar5,puVar5[1],puVar5[2],puVar5[3]);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x11c00000,DAT_00494b48,DAT_00494b48,uVar3,uVar6,puVar5 + 9,*puVar5,
                            puVar5[1],puVar5[2],puVar5[3]);
      }
    }
    else if (bVar1 == 2) {
      puVar5 = *(undefined4 **)(param_1 + 0xc);
      uVar3 = puVar5[4];
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00494480,DAT_0049447c,DAT_00494b44,0x249,DAT_00494b40,puVar2,uVar3,
                     puVar5 + 5,*puVar5,puVar5[1],puVar5[2],puVar5[3]);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x11c00000,DAT_00494b48,DAT_00494b48,puVar2,uVar3,puVar5 + 5,*puVar5,
                            puVar5[1],puVar5[2],puVar5[3]);
      }
    }
    else if (bVar1 < 2) {
      puVar5 = *(undefined4 **)(param_1 + 0xc);
      uVar3 = puVar5[8];
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00494480,DAT_0049447c,DAT_00494b44,0x23e,DAT_00494b40,uVar6,uVar3,
                     puVar5 + 9,*puVar5,puVar5[1],puVar5[2],puVar5[3]);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x11c00000,DAT_00494b48,DAT_00494b48,uVar6,uVar3,puVar5 + 9,*puVar5,
                            puVar5[1],puVar5[2],puVar5[3]);
      }
    }
    uVar3 = 0;
  }
  return uVar3;
}

