
undefined8 FUN_0047075c(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if (*DAT_004708a4 == 0) {
    iVar1 = 2;
  }
  else if ((param_1 & 0xfff) == 0) {
    if (param_1 < 0x2000000) {
      FUN_0046f65e();
      FUN_00470f68();
      iVar1 = FUN_004703ba();
      if (iVar1 == 0) {
        iVar1 = FUN_00470670();
        if (iVar1 == 0) {
          param_2 = 0;
          iVar1 = FUN_0047021c(0x20,param_1,1,0);
          if (iVar1 == 0) {
            iVar1 = FUN_004703ba();
            if (iVar1 == 0) {
              iVar1 = FUN_004706e0();
              if (iVar1 != 0) {
                FUN_004733ee(DAT_004710a8,param_1,iVar1);
              }
            }
            else {
              FUN_004733ee(DAT_004710a4,param_1);
              iVar1 = 4;
            }
          }
          else {
            FUN_004733ee(DAT_0047101c,param_1,iVar1);
          }
        }
        else {
          FUN_004733ee(DAT_00471018,param_1,iVar1);
        }
      }
      else {
        FUN_004733ee(DAT_00471014,param_1);
        iVar1 = 3;
      }
      FUN_00470e90();
      FUN_0046f674();
    }
    else {
      iVar1 = 5;
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0x40e;
      FUN_0043d574(2,DAT_00470a7c,DAT_00470a78,DAT_00470f64,0x40e,DAT_00470f60,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_00471010,DAT_00471010);
    }
    iVar1 = 6;
  }
  return CONCAT44(param_2,iVar1);
}

