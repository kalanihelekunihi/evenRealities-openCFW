
undefined8 FUN_004700b4(uint *param_1,uint param_2,undefined4 param_3,int param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  uint local_18;
  undefined4 local_14;
  int local_10;
  
  local_18 = param_2;
  if (param_1 == (uint *)0x0) {
    uVar1 = 0xffffffff;
  }
  else {
    local_14 = param_3;
    local_10 = param_4;
    if ((*DAT_004708a4 == 0) && (iVar2 = FUN_0046fe38(), iVar2 != 0)) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_14 = DAT_004709b8;
        local_18 = 0x2ed;
        local_10 = iVar2;
        FUN_0043d574(1,DAT_00470a7c,DAT_00470a78,DAT_004709bc);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_00470a80,DAT_00470a80,iVar2);
      }
      uVar1 = 0xfffffffd;
    }
    else {
      FUN_0046f65e();
      FUN_00470f68();
      local_18 = 0;
      iVar2 = FUN_00470028(&local_18);
      FUN_00470e90();
      FUN_0046f674();
      if (iVar2 == 0) {
        *param_1 = local_18 & 0xffffff;
        uVar1 = 0;
      }
      else {
        uVar1 = 0xfffffffe;
      }
    }
  }
  return CONCAT44(local_18,uVar1);
}

