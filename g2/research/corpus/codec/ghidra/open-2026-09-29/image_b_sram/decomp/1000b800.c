
undefined4 FUN_1000b800(void)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uStack_2c;
  undefined2 uStack_28;
  undefined2 uStack_26;
  undefined2 uStack_24;
  undefined *puStack_20;
  undefined *puStack_1c;
  undefined *puStack_18;
  undefined *puStack_14;
  
  uStack_28 = 0x23;
  uStack_26 = 0x2d;
  uStack_24 = 0x37;
  puStack_20 = PTR_FUN_1000b8e8;
  uStack_2c = 1;
  puStack_1c = PTR_LAB_1000b8ec;
  puStack_18 = PTR_LAB_1000b8f0;
  puStack_14 = PTR_LAB_1000b8f4;
  FUN_1000deb4(&puStack_20);
  iVar2 = FUN_1000de40(2,3,16000,0,1,0,0,DAT_1000b8fc,DAT_1000b8f8,0,1,&uStack_2c);
  piVar1 = DAT_1000b908;
  *DAT_1000b908 = iVar2;
  if (iVar2 == 0) {
    FUN_10009934(PTR_s__LVP_MODE_DENOISE_Init_Beamformi_1000b910);
    uVar3 = 0xffffffff;
  }
  else {
    FUN_1000c6e8(iVar2,3,&uStack_28);
    iVar2 = FUN_10009f2c(0x800);
    piVar1[1] = iVar2;
    if (iVar2 == 0) {
      FUN_10009934(PTR_s__LVP_MODE_DENOISE_BF_malloc_g_bf_1000b918);
      uVar3 = 0xffffffff;
    }
    else {
      uVar3 = FUN_1000c6a4(2,3,0x200,0x100);
      FUN_10009934(PTR_s_bf_size____d_1000b90c,uVar3);
      iVar2 = FUN_10009f2c(uVar3);
      if (iVar2 == 0) {
        FUN_10009934(PTR_s__LVP_MODE_DENOISE_BF_malloc_g_bf_1000b914);
        uVar3 = 0xffffffff;
      }
      else {
        FUN_1000d1fc(*piVar1,iVar2);
        uVar3 = 0;
      }
    }
  }
  return uVar3;
}

