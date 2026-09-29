
undefined8 FUN_00482dd8(uint param_1,uint param_2,byte param_3)

{
  undefined4 local_14;
  
  local_14 = CONCAT31(CONCAT21(CONCAT11(local_14._3_1_,
                                        (char)(((uint)param_3 * (param_1 >> 0x10 & 0xff) +
                                               (0xff - (uint)param_3) * (param_2 >> 0x10 & 0xff)) *
                                               0x8081 >> 0x17)),
                               (char)(((uint)param_3 * (param_1 >> 8 & 0xff) +
                                      (0xff - (uint)param_3) * (param_2 >> 8 & 0xff)) * 0x8081 >>
                                     0x17)),
                      (char)(((uint)param_3 * (param_1 & 0xff) +
                             (0xff - (uint)param_3) * (param_2 & 0xff)) * 0x8081 >> 0x17));
  return CONCAT44(local_14,local_14);
}

