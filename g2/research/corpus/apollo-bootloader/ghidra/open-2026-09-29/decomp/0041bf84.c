
int FUN_0041bf84(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  char *pcVar2;
  int iVar3;
  undefined4 local_28;
  uint *local_24;
  uint local_20;
  uint *local_1c;
  uint local_18;
  uint local_14;
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  iVar3 = FUN_0041b8f8(&local_24,param_1);
  if (iVar3 == 0) {
    if ((*local_24 & local_20) == 0) {
      if ((param_1 == 0x17) && (-1 < *DAT_0041c4ac << 4)) {
        iVar3 = 1;
      }
      else {
        FUN_0041cd34();
        if (param_1 == 0x14) {
          if (*DAT_0041c490 == '\x03') {
            FUN_0041bae8(3);
          }
          clock_request(4,0x14);
          pcVar2 = DAT_0041c48c;
          if (*DAT_0041c48c == '\x03') {
            clock_request(5,0x14);
          }
          if (*pcVar2 == '\0') {
            local_28 = CONCAT31(local_28._1_3_,1);
          }
          else {
            local_28 = CONCAT31(local_28._1_3_,2);
          }
          FUN_0041cd1a(1,1,&local_28);
        }
        else {
          if (((local_20 & 0x3fffffff) != 0) && (param_1 < 0x1e)) {
            FUN_0041cd1a(3,1,&local_18);
          }
          if (((local_20 & 0x4c4) != 0) && (0x1d < param_1)) {
            FUN_0041cd1a(4,1,&local_18);
          }
        }
        local_14 = critical_save();
        *local_24 = *local_24 | local_20;
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          enableIRQinterrupts((local_14 & 1) == 1);
        }
        FUN_0041cd4a(local_14);
        local_28 = 1;
        iVar3 = delay_us_status_check(5,local_1c,local_18,local_18);
        if (iVar3 == 0) {
          if (param_1 == 0x17) {
            iVar3 = delay_status_change(100,DAT_0041cafc,1,1);
            if (iVar3 != 0) {
              return iVar3;
            }
            clock_request(4,0x17);
          }
          if (param_1 == 0x1d) {
            delay_us(100);
          }
          if ((*local_1c & local_18) == 0) {
            iVar3 = 1;
          }
          else {
            iVar3 = 0;
          }
        }
      }
    }
    else {
      iVar3 = 0;
    }
  }
  return iVar3;
}

