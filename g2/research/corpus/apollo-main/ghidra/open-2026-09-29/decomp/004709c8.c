
undefined8 FUN_004709c8(uint param_1,int param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  if (((*DAT_004710ac == 0) || (param_2 == 0)) || (param_3 == 0)) {
    iVar1 = 6;
  }
  else if (param_1 < 0x2000000) {
    iVar2 = param_3;
    FUN_0046f65e();
    FUN_00470f68();
    iVar1 = FUN_004703ba();
    if (iVar1 == 0) {
      iVar1 = FUN_00470168(3,param_1,1,param_2,param_3,param_4);
      if (iVar1 == 0) {
        FUN_004703ba();
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          param_3 = 0x506;
          FUN_0043d574(2,DAT_00470a7c,DAT_00470a78,DAT_004710d0,0x506,DAT_004710cc);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_004710d4,DAT_004710d4);
        }
      }
    }
    else {
      FUN_004733ee(DAT_00470d5c);
      iVar1 = 3;
      param_3 = iVar2;
    }
    FUN_00470e90();
    FUN_0046f674();
  }
  else {
    iVar1 = 5;
  }
  return CONCAT44(param_3,iVar1);
}

