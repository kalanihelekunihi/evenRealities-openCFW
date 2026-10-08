"""Preserve existing TX suite's RX cuts at relocated native RX symbols."""
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[5]
p=ROOT/'g2/components/bootloader/initializer_callbacks/verify_elog_uart_tx.py';s=importlib.util.spec_from_file_location('tx',p);tx=importlib.util.module_from_spec(s);s.loader.exec_module(tx);original=tx.Machine.code

def code(self,uc,pc,size,user):
 if self.source:
  for name,stock in [('opencfw_boot_uart_rx_blocking',0x42348e),('opencfw_boot_uart_rx_start',0x4234fa)]:
   if pc==(self.symbols[name]&~1):
    self.events.append(['rx-cut',hex(stock),uc.reg_read(tx.a.UC_ARM_REG_R0)]);uc.reg_write(tx.a.UC_ARM_REG_R0,7);uc.reg_write(tx.a.UC_ARM_REG_PC,uc.reg_read(tx.a.UC_ARM_REG_LR));return
 original(self,uc,pc,size,user)
tx.Machine.code=code
if __name__=='__main__':tx.main()
