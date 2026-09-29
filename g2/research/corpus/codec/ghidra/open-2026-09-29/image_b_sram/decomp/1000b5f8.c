
undefined4 FUN_1000b5f8(uint *param_1)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint *puVar4;
  undefined *local_1c;
  undefined *puStack_18;
  undefined *puStack_14;
  undefined *puStack_10;
  
  if (param_1 != (uint *)0x0) {
    uVar2 = *param_1;
    puVar4 = DAT_1000b6c8;
    if ((((uVar2 & 0xff) == 0) || (puVar4 = DAT_1000b6e4, (uVar2 & 0xff) == 1)) &&
       ((puVar4[2] = uVar2, puVar4[3] == 0 || (param_1[3] != 0)))) {
      uVar3 = param_1[2];
      if (param_1[2] == 0) {
        uVar3 = DAT_1000b6cc;
      }
      *puVar4 = uVar3;
      puVar4[4] = param_1[1];
      FUN_10004708(uVar2);
      FUN_10004724(puVar4[2]);
      iVar1 = FUN_1000451c(puVar4[2],puVar4[4]);
      if (iVar1 == 0) {
        if ((DAT_1000b6c8[3] == 0) || (DAT_1000b6c8[0x62] == 0)) {
          FUN_10009fa8(DAT_1000b6ec,DAT_1000b6e8,0x100,0x20);
        }
        if (puVar4[3] == 0) {
          FUN_10009fa8(puVar4 + 0x57,puVar4 + 0x17,0x100,0x20);
        }
        FUN_100046ac(puVar4[2],PTR_LAB_1000b6d0,0);
        local_1c = PTR_LAB_1000b6d4;
        puStack_18 = PTR_s_UartMessageAsyncSuspend_1000b6d8;
        puStack_14 = PTR_LAB_1000b6dc;
        puStack_10 = PTR_s_UartMessageAsyncResume_1000b6e0;
        FUN_1000a784(&local_1c);
        FUN_1000a7f0(&puStack_14);
        FUN_1000a85c(puVar4 + 0x5e);
        puVar4[3] = 1;
        return 0;
      }
    }
  }
  return 0xffffffff;
}

