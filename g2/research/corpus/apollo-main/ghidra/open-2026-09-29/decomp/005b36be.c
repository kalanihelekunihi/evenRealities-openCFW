
undefined4 FUN_005b36be(byte param_1,char param_2)

{
  undefined4 unaff_r7;
  
  if ((param_1 != 0) && (param_1 < 4)) {
    if (param_2 == '\x01') {
      if (*(int *)(PTR_DAT_005b3e2c + (uint)param_1 * 8) != 0) {
        (**(code **)(PTR_DAT_005b3e2c + (uint)param_1 * 8))();
      }
    }
    else if ((param_2 == '\x02') && (*(int *)(PTR_DAT_005b3e2c + (uint)param_1 * 8 + 4) != 0)) {
      (**(code **)(PTR_DAT_005b3e2c + (uint)param_1 * 8 + 4))();
    }
  }
  return unaff_r7;
}

