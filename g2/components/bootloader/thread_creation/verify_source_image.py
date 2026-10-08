#!/usr/bin/env python3
"""Normal/update validation for the strongest source-linked test image."""
import importlib.util,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('platform_profile',HERE/'verify_dfu_storage_platform.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p);p.LOCAL_PROVIDERS={'opencfw_boot_coprocessor_enable':0x41ac44,'opencfw_boot_fp_lazy_mode':0x41ac5a,'opencfw_boot_delay_scaled':0x41f9d8,'opencfw_boot_delay_raw':0x41f9e6,'opencfw_boot_delay_us_math':0x41d1c0,'opencfw_boot_icache_enable':0x41e1e8,'opencfw_boot_dcache_enable':0x41e266,'opencfw_read_mspi_register_id':0x41d90e,'opencfw_publish_mspi_mode':0x41fadc};p.NATIVE_DELAY_MATH=True;p.NATIVE_DEVICE_INFO=True
def main():
 p.main();out=Path(sys.argv[sys.argv.index('--output')+1]);r=json.loads(out.read_text());r['image_role']='Source-linked test image; native error transaction also linked, separately exercised by verify_source_image_failures.py. Not a standalone physical payload.';out.write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
