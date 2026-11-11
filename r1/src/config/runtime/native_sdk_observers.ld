/* Section-relative ranges for SDK users of the shared legacy iterator.
 * A range owns only its existing C records. Empty ranges remain empty. */
SECTIONS
{
 .sdh_req_observers0 0 : ALIGN(4)
 {
  __start_sdh_req_observers0 = .;
  KEEP(*(.sdh_req_observers0 .sdh_req_observers0.*))
  __stop_sdh_req_observers0 = .;
 }
 .sdh_req_observers1 0 : ALIGN(4)
 {
  __start_sdh_req_observers1 = .;
  KEEP(*(.sdh_req_observers1 .sdh_req_observers1.*))
  __stop_sdh_req_observers1 = .;
 }
 .sdh_state_observers0 0 : ALIGN(4)
 {
  __start_sdh_state_observers0 = .;
  KEEP(*(.sdh_state_observers0 .sdh_state_observers0.*))
  __stop_sdh_state_observers0 = .;
 }
 .sdh_state_observers1 0 : ALIGN(4)
 {
  __start_sdh_state_observers1 = .;
  KEEP(*(.sdh_state_observers1 .sdh_state_observers1.*))
  __stop_sdh_state_observers1 = .;
 }
 .sdh_stack_observers0 0 : ALIGN(4)
 {
  __start_sdh_stack_observers0 = .;
  KEEP(*(.sdh_stack_observers0 .sdh_stack_observers0.*))
  __stop_sdh_stack_observers0 = .;
 }
 .sdh_stack_observers1 0 : ALIGN(4)
 {
  __start_sdh_stack_observers1 = .;
  KEEP(*(.sdh_stack_observers1 .sdh_stack_observers1.*))
  __stop_sdh_stack_observers1 = .;
 }
 .sdh_soc_observers0 0 : ALIGN(4)
 {
  __start_sdh_soc_observers0 = .;
  /* Stock clock observer precedes fstorage within priority zero. */
  KEEP(*nrf_drv_clock.c.o(.sdh_soc_observers0))
  KEEP(*(.sdh_soc_observers0 .sdh_soc_observers0.*))
  __stop_sdh_soc_observers0 = .;
 }
 .sdh_soc_observers1 0 : ALIGN(4)
 {
  __start_sdh_soc_observers1 = .;
  KEEP(*(.sdh_soc_observers1 .sdh_soc_observers1.*))
  __stop_sdh_soc_observers1 = .;
 }
 .pwr_mgmt_data0 0 : ALIGN(4)
 {
  __start_pwr_mgmt_data0 = .;
  KEEP(*(.pwr_mgmt_data0 .pwr_mgmt_data0.*))
  __stop_pwr_mgmt_data0 = .;
 }
 .pwr_mgmt_data1 0 : ALIGN(4)
 {
  __start_pwr_mgmt_data1 = .;
  KEEP(*(.pwr_mgmt_data1 .pwr_mgmt_data1.*))
  __stop_pwr_mgmt_data1 = .;
 }
 .pwr_mgmt_data2 0 : ALIGN(4)
 {
  __start_pwr_mgmt_data2 = .;
  KEEP(*(.pwr_mgmt_data2 .pwr_mgmt_data2.*))
  __stop_pwr_mgmt_data2 = .;
 }
}
ASSERT((SIZEOF(.sdh_req_observers0) % 8) == 0, "sdh_req_observers0: incomplete record")
ASSERT((SIZEOF(.sdh_req_observers1) % 8) == 0, "sdh_req_observers1: incomplete record")
ASSERT((SIZEOF(.sdh_state_observers0) % 8) == 0, "sdh_state_observers0: incomplete record")
ASSERT((SIZEOF(.sdh_state_observers1) % 8) == 0, "sdh_state_observers1: incomplete record")
ASSERT((SIZEOF(.sdh_stack_observers0) % 8) == 0, "sdh_stack_observers0: incomplete record")
ASSERT((SIZEOF(.sdh_stack_observers1) % 8) == 0, "sdh_stack_observers1: incomplete record")
ASSERT((SIZEOF(.sdh_soc_observers0) % 8) == 0, "sdh_soc_observers0: incomplete record")
ASSERT((SIZEOF(.sdh_soc_observers1) % 8) == 0, "sdh_soc_observers1: incomplete record")
ASSERT((SIZEOF(.pwr_mgmt_data0) % 4) == 0, "pwr_mgmt_data0: incomplete record")
ASSERT((SIZEOF(.pwr_mgmt_data1) % 4) == 0, "pwr_mgmt_data1: incomplete record")
ASSERT((SIZEOF(.pwr_mgmt_data2) % 4) == 0, "pwr_mgmt_data2: incomplete record")
