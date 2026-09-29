
undefined4 SVC_NvdbGetSysData(byte param_1)

{
  undefined4 uVar1;
  
  uVar1 = DAT_004aff98;
  if (((((param_1 != 0) && (uVar1 = DAT_004affa0, param_1 != 2)) &&
       (uVar1 = DAT_004aff9c, 1 < param_1)) &&
      (((uVar1 = DAT_004affa8, param_1 != 4 && (uVar1 = DAT_004affa4, 3 < param_1)) &&
       ((uVar1 = DAT_004afcd8, param_1 != 6 &&
        ((uVar1 = DAT_004affac, 5 < param_1 && (uVar1 = DAT_004aff6c, param_1 != 8)))))))) &&
     ((uVar1 = DAT_004aff60, 7 < param_1 &&
      ((((uVar1 = DAT_004affb4, param_1 != 10 && (uVar1 = DAT_004affb0, 9 < param_1)) &&
        (uVar1 = DAT_004affbc, param_1 != 0xc)) && (uVar1 = DAT_004affb8, 0xb < param_1)))))) {
    uVar1 = DAT_004af880;
  }
  return uVar1;
}

