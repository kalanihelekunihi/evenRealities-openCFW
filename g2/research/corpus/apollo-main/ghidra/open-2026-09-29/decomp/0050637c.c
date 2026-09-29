
undefined8 FUN_0050637c(undefined4 param_1,char param_2,undefined1 *param_3,undefined4 param_4)

{
  byte bVar1;
  undefined4 uVar2;
  undefined4 local_10;
  
  if (param_2 == '\0') {
    uVar2 = 0x16;
  }
  else {
    if (param_2 != '\x01') {
      uVar2 = 0xfffffff5;
      local_10 = param_4;
      goto LAB_0050648e;
    }
    uVar2 = 0x56;
  }
  local_10._1_3_ = (undefined3)((uint)param_4 >> 8);
  local_10 = CONCAT31(local_10._1_3_,*param_3) & 0xffffff01;
  local_10 = CONCAT22(local_10._2_2_,
                      CONCAT11(param_3[8],
                               (byte)local_10 | (param_3[1] & 1) << 1 | (param_3[2] & 1) << 2 |
                               (param_3[3] & 1) << 3 | (param_3[4] & 1) << 4 | (param_3[5] & 1) << 5
                               | (param_3[6] & 1) << 6 | param_3[7] << 7)) & 0xffff01ff;
  bVar1 = local_10._1_1_ | (param_3[9] & 1) << 1;
  local_10._0_2_ =
       CONCAT11(bVar1 | (param_3[10] & 1) << 2 | (param_3[0xb] & 1) << 3 | (param_3[0xc] & 1) << 4 |
                (param_3[0xd] & 1) << 5 | (param_3[0xe] & 1) << 6,(byte)local_10);
  uVar2 = FUN_00508e74(param_1,uVar2,2,&local_10);
LAB_0050648e:
  return CONCAT44(local_10,uVar2);
}

