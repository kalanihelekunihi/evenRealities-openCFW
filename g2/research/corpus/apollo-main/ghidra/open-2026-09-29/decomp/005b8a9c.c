
uint FUN_005b8a9c(float param_1,byte param_2,uint param_3,int param_4,uint param_5)

{
  float fVar1;
  uint local_10;
  
  local_10 = param_5;
  if ((param_4 != 0) && (param_5 != 0)) {
    if (param_2 == 9) {
      if (param_3 == 0) {
        FUN_0044b728(param_4,param_5,&DAT_005b8d1c);
      }
      else {
        local_10 = (param_3 % 0xe10) / 0x168;
        FUN_0044b728(param_4,param_5,DAT_005b8d88,param_3 / 0xe10);
      }
    }
    else if (0.0 < param_1) {
      if (param_2 == 5) {
        FUN_0044b728(param_4,param_5,&DAT_005b8d94,(int)param_1);
      }
      else {
        if (4 < param_2) {
          if ((param_2 == 7) || (param_2 < 7)) {
            if ((int)((uint)(param_1 < DAT_005b8da4) << 0x1f) < 0) {
              FUN_0044b728(param_4,param_5,&DAT_005b8d94,(int)param_1);
              return param_5;
            }
            if ((int)((uint)(param_1 < DAT_005b8d98) << 0x1f) < 0) {
              fVar1 = param_1 / DAT_005b8d9c;
              FUN_0044b728(param_4,param_5,DAT_005b8da0,(int)(param_1 / DAT_005b8da4));
              return (int)fVar1 % 10;
            }
            FUN_0044b728(param_4,param_5,&DAT_005b8da8,(int)(param_1 / DAT_005b8da4));
            return param_5;
          }
          if (param_2 == 8) {
            if (DAT_005b8d9c <= param_1) {
              FUN_0044b728(param_4,param_5,DAT_005b8d8c);
              return param_5;
            }
            FUN_0044b728(param_4,param_5,DAT_005b8d90,(int)param_1);
            return param_5;
          }
        }
        FUN_0044b728(param_4,param_5,&DAT_005b8d1c);
      }
    }
    else {
      FUN_0044b728(param_4,param_5,&DAT_005b8d1c);
    }
  }
  return local_10;
}

