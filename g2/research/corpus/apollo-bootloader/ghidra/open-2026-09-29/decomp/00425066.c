
undefined4 am_hal_mspi_enable(uint *param_1)

{
  undefined4 uVar1;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_004251b0)) {
    uVar1 = 2;
  }
  else if ((char)param_1[2] == '\0') {
    uVar1 = 7;
  }
  else {
    if (param_1[6] != 0) {
      param_1[7] = 0;
      param_1[8] = 0;
      mspi_cq_init(param_1[1],param_1[5],param_1[6]);
      *(undefined4 *)(DAT_004251a4 + param_1[1] * 0x1000 + 0x2b4) = DAT_004251bc;
      param_1[0x215] = 0;
      *(undefined1 *)(param_1 + 0x20f) = 0;
      param_1[0x211] = 0;
      param_1[0x20e] = 0;
      param_1[0x210] = 0;
      *(undefined1 *)(param_1 + 0x20b) = 0;
      param_1[0x20c] = 0;
      *(undefined1 *)((int)param_1 + 0x82d) = 1;
      param_1[0x217] = 0;
    }
    *param_1 = *param_1 | 0x2000000;
    uVar1 = 0;
  }
  return uVar1;
}

