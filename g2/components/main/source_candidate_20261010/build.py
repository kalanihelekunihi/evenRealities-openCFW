#!/usr/bin/env python3
"""Compile the source-owned main candidates; never reads a firmware oracle."""
from pathlib import Path
import hashlib
import json
import shlex
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'g2/build/source-candidates/20261010-main'
SOURCES = [
    'g2/components/main/iar_runtime_candidates_20261010/runtime.c',
    'g2/components/main/smp_dispatch_candidates_20261010/smp_dispatch.c',
    'g2/components/main/flashdb_candidates_20261010/blob_read.c',
    'g2/components/main/flashdb_shortlog_adapter_20261010/adapter.c',
    'g2/components/main/flashdb_literal_candidates_20261010/literals.c',
    'g2/components/main/flashdb_get_blob_candidates_20261010/get_blob.c',
    'g2/components/main/flashdb_db_path_candidates_20261010/db_path.c',
    'g2/components/main/flashdb_get_kv_candidates_20261010/get_kv.c',
    'g2/components/main/flashdb_flash_read_candidates_20261010/flash_read.c',
    'g2/components/main/flashdb_find_kv_candidates_20261010/find_kv.c',
    'g2/components/main/flashdb_cache_update_candidates_20261010/cache_update.c',
    'g2/components/main/flashdb_crc32_candidates_20261010/crc32.c',
    'g2/components/main/flashdb_cache_lookup_candidates_20261010/cache_lookup.c',
    'g2/components/main/flashdb_find_no_cache_candidates_20261010/find_no_cache.c',
    'g2/components/main/flashdb_kv_iterator_candidates_20261010/kv_iterator.c',
    'g2/components/main/flashdb_next_sector_candidates_20261010/next_sector.c',
    'g2/components/main/flashdb_next_kv_candidates_20261010/next_kv.c',
    'g2/components/main/flashdb_magic_scan_candidates_20261010/magic_scan.c',
    'g2/components/main/flashdb_sector_cache_lookup_candidates_20261010/sector_cache_lookup.c',
    'g2/components/main/flashdb_read_kv_candidates_20261010/read_kv.c',
    'g2/components/main/flashdb_get_status_candidates_20261010/get_status.c',
    'g2/components/main/flashdb_write_status_candidates_20261010/write_status.c',
    'g2/components/main/flashdb_read_sector_candidates_20261010/read_sector.c',
    'g2/components/main/flashdb_sector_cache_update_candidates_20261010/sector_cache_update.c',
    'g2/components/main/flashdb_continue_ff_candidates_20261010/continue_ff.c',
    'g2/components/main/flashdb_flash_write_candidates_20261010/flash_write.c',
    'g2/components/main/flashdb_partition_read_candidates_20261010/partition_read.c',
    'g2/components/main/flashdb_partition_write_candidates_20261010/partition_write.c',
    'g2/components/main/fal_device_selector_candidates_20261010/device_selector.c',
    'g2/components/main/fal_partition_state_candidates_20261010/partition_state.c',
    'g2/components/main/fal_device_find_candidates_20261010/device_find.c',
    'g2/components/main/fal_product_config_candidates_20261013/product_tables.c',
    'g2/components/main/fal_norflash_init_candidates_20261013/norflash_init.c',
    'g2/components/main/fal_norflash_read_candidates_20261013/read.c',
    'g2/components/main/fal_norflash_write_candidates_20261013/write.c',
    'g2/components/main/fal_norflash_erase_candidates_20261013/erase.c',
    'g2/components/main/fal_norflash_erase_lower_candidates_20261013/sector_erase.c',
    'g2/components/main/fal_norflash_wait_idle_candidates_20261013/wait_idle.c',
    'g2/components/main/fal_norflash_wait_status_candidates_20261013/wait_status.c',
    'g2/components/main/fal_norflash_delay_candidates_20261013/delay.c',
    'g2/components/main/fal_norflash_status_query_candidates_20261013/status_query.c',
    'g2/components/main/fal_norflash_command_candidates_20261013/command.c',
    'g2/components/main/fal_norflash_write_latch_candidates_20261013/write_latch.c',
    'g2/components/main/fal_norflash_write_command_candidates_20261013/write_command.c',
    'g2/components/main/fal_norflash_mspi_transfer_candidates_20261013/transfer.c',
    'g2/components/main/mspi_status_poll_candidates_20261013/poll.c',
    'g2/components/main/mspi_fifo_candidates_20261013/fifo.c',
    'g2/components/main/fal_norflash_mode_select_candidates_20261013/mode_select.c',
    'g2/components/main/fal_norflash_entry_exit_candidates_20261013/entry_exit.c',
    'g2/components/main/fal_norflash_serial_validator_candidates_20261013/validator.c',
    'g2/components/main/mspi_enable_disable_candidates_20261013/enable_disable.c',
    'g2/components/main/mspi_cq_wrappers_candidates_20261013/wrappers.c',
    'g2/components/main/mspi_cq_disable_provider_candidates_20261013/disable.c',
    'g2/components/main/mspi_cq_term_provider_candidates_20261013/term.c',
    'g2/components/main/mspi_cq_index_refresh_candidates_20261013/refresh.c',
    'g2/components/main/mspi_cq_init_provider_candidates_20261013/init.c',
    'g2/components/main/mspi_cq_enable_provider_candidates_20261013/enable.c',
    'g2/components/main/nor_clock_select_candidates_20261013/clock_select.c',
    'g2/components/main/clock_request_candidates_20261013/clock_request.c',
    'g2/components/main/nor_controller_sram_candidates_20261013/controller_word.c',
    'g2/components/main/mspi_handle_init_candidates_20261013/init.c',
    'g2/components/main/mspi_handle_config_candidates_20261013/config.c',
    'g2/components/main/mspi_configure_candidates_20261013/configure.c',
    'g2/components/main/mspi_configure_finish_candidates_20261013/finish.c',
    'g2/components/main/mspi_clock_route_candidates_20261013/route.c',
    'g2/components/main/mspi_clock_dispatch_candidates_20261013/dispatch.c',
    'g2/components/main/clock_request_bitmap_candidates_20261013/bitmap.c',
    'g2/components/main/clock_release_45_candidates_20261013/release.c',
    'g2/components/main/clock_release_01_candidates_20261013/release.c',
    'g2/components/main/clock_release_3_candidates_20261013/release.c',
    'g2/components/main/clock_release_2_candidates_20261013/release.c',
    'g2/components/main/clock_acquire_013_candidates_20261013/acquire.c',
    'g2/components/main/clock_release_6_candidates_20261013/release.c',
    'g2/components/main/queue_uninit_candidates_20261013/uninit.c',
    'g2/components/main/irq_enable_candidates_20261013/enable.c',
    'g2/components/main/clock_acquire_6_candidates_20261013/acquire.c',
    'g2/components/main/queue_init_candidates_20261013/init.c',
    'g2/components/main/queue_enable_candidates_20261013/enable.c',
    'g2/components/main/queue_config_candidates_20261013/config.c',
    'g2/components/main/queue_start_candidates_20261013/start.c',
    'g2/components/main/clock_class2_helpers_candidates_20261013/helpers.c',
    'g2/components/main/clock_mode_set_candidates_20261013/mode.c',
    'g2/components/main/clock_acquire_2_candidates_20261013/acquire.c',
    'g2/components/main/clock_power_leaf_candidates_20261013/power.c',
    'g2/components/main/clock_class4_acquire_candidates_20261013/acquire.c',
    'g2/components/main/clock_class4_trigger_candidates_20261013/trigger.c',
    'g2/components/main/clock_class5_config_candidates_20261013/config.c',
    'g2/components/main/clock_class5_finish_candidates_20261013/finish.c',
    'g2/components/main/clock_class5_acquire_candidates_20261013/acquire.c',
    'g2/components/main/mspi_aux_config_candidates_20261013/aux.c',
    'g2/components/main/mspi_transfer_mode16_candidates_20261013/mode16.c',
    'g2/components/main/mspi_transfer_mode26_candidates_20261013/mode26.c',
    'g2/components/main/mspi_mode_update_candidates_20261013/update.c',
    'g2/components/main/mspi_transfer_mode24_candidates_20261013/mode24.c',
    'g2/components/main/mspi_transfer_basic_candidates_20261013/basic.c',
    'g2/components/main/mspi_transfer_structured_candidates_20261013/structured.c',
    'g2/components/main/mspi_transfer_control_candidates_20261013/control.c',
    'g2/components/main/mspi_transfer_queue_state_candidates_20261013/queue_state.c',
    'g2/components/main/mspi_transfer_aux_candidates_20261013/aux_transfer.c',
    'g2/components/main/mspi_queue_terminate_candidates_20261013/terminate.c',
    'g2/components/main/mspi_queue_descriptor_candidates_20261013/descriptor.c',
    'g2/components/main/mspi_queue_activate_candidates_20261013/activate.c',
    'g2/components/main/queue_reset_candidates_20261013/reset.c',
    'g2/components/main/mspi_transfer_queue_mode_candidates_20261013/mode.c',
    'g2/components/main/mspi_queue_flags_candidates_20261013/flags.c',
    'g2/components/main/mspi_queue_start_candidates_20261013/start.c',
    'g2/components/main/mspi_cq_commit_candidates_20261013/commit.c',
    'g2/components/main/mspi_cq_reserve_candidates_20261013/reserve.c',
    'g2/components/main/mspi_transfer_submit_candidates_20261013/submit.c',
    'g2/components/main/mspi_transfer_descriptor_candidates_20261013/descriptor.c',
    'g2/components/main/mspi_transfer_dispatch_candidates_20261013/dispatch.c',
    'g2/components/main/nor_read_lower_candidates_20261013/read_lower.c',
    'g2/components/main/nor_write_lower_candidates_20261013/write_lower.c',
    'g2/components/main/flashdb_print_wrapper_candidates_20261010/print_wrapper.c',
    'g2/components/main/diagnostic_flags_candidates_20261010/flags.c',
    'g2/components/main/kernel_tick_candidates_20261010/tick.c',
    'g2/components/main/smp_provider_candidates_20261010/compare.c',
    'g2/components/main/wsf_queue_candidates_20261010/wsf_queue.c',
    'g2/components/main/wsf_buffer_candidates_20261010/buffer_free.c',
    'g2/components/main/smp_ccb_candidates_20261010/ccb_lookup.c',
    'g2/components/main/smp_db_candidates_20261010/db_service.c',
    'g2/components/main/wsf_trace_candidates_20261010/trace.c',
    'g2/components/main/extended_log_helpers_20261010/guard.c',
    'g2/components/main/smp_sm_dispatch_tail_20261010/dispatch_tail.c',
    'g2/components/main/smp_sm_execute_candidates_20261010/execute.c',
    'g2/components/main/extended_log_policy_candidates_20261010/policy.c',
    'g2/components/main/extended_log_append_candidates_20261010/append.c',
    'g2/components/main/extended_log_output_candidates_20261010/output.c',
    'g2/components/main/extended_log_memory_candidates_20261010/memory.c',
    'g2/components/main/extended_log_token_candidates_20261010/token.c',
    'g2/components/main/extended_log_time_candidates_20261010/time.c',
    'g2/components/main/extended_log_postformat_candidates_20261010/postformat.c',
    'g2/components/main/extended_log_smp_format_candidates_20261010/smp_format.c',
    'g2/components/main/extended_log_common_format_candidates_20261010/common_format.c',
    'g2/components/main/extended_log_smp_quiet_candidates_20261010/quiet.c',
    'g2/components/main/extended_log_smp_onebit_candidates_20261010/onebit.c',
    'g2/components/main/extended_log_module_policy_candidates_20261010/module_policy.c',
    'g2/components/main/extended_log_smp_abi_candidates_20261010/abi.c',
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args):
    return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.STDOUT)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cc = run(['xcrun', '--find', 'clang']).strip()
    ar = shutil.which('arm-none-eabi-ar')
    ld = shutil.which('arm-none-eabi-ld')
    nm = shutil.which('arm-none-eabi-nm')
    if not all((ar, ld, nm)):
        raise SystemExit('ARM binutils ar, ld and nm are required')
    flags = ['--target=arm-none-eabi', '-mcpu=cortex-m55', '-mthumb',
             '-std=c11', '-Oz', '-ffreestanding', '-fno-builtin',
             '-ffunction-sections', '-fdata-sections', '-Wall', '-Wextra', '-Werror']
    objects, commands, inputs, tool_headers = [], [], {}, {}
    for source in SOURCES:
        src = ROOT / source
        obj = OUT / (src.parent.name + '.o')
        dep = obj.with_suffix('.d')
        cmd = [cc, *flags, '-MD', '-MF', str(dep), '-c', str(src), '-o', str(obj)]
        run(cmd)
        commands.append(cmd)
        objects.append(obj)
        dependencies = shlex.split(dep.read_text().split(':', 1)[1].replace('\\\n', ' '))
        for filename in dependencies:
            path = Path(filename).resolve()
            if path.is_relative_to(ROOT):
                key = str(path.relative_to(ROOT))
                if not key.startswith('g2/components/main/'):
                    raise RuntimeError('Unexpected repository dependency: ' + key)
                inputs[key] = digest(path)
            else:
                tool_headers[str(path)] = digest(path)
    archive = OUT / 'main-candidates.a'
    if archive.exists():
        archive.unlink()  # Only this build's generated archive is replaced.
    archive_cmd = [ar, 'rcsD', str(archive), *map(str, objects)]
    run(archive_cmd)
    commands.append(archive_cmd)
    combined = OUT / 'main-candidates.o'
    link_cmd = [ld, '-r', '-o', str(combined), *map(str, objects)]
    run(link_cmd)
    commands.append(link_cmd)
    undefined = run([nm, '-u', str(combined)])
    defined = run([nm, '--defined-only', str(combined)])
    (OUT / 'undefined-symbols.txt').write_text(undefined)
    (OUT / 'defined-symbols.txt').write_text(defined)
    receipt = {
        'status': 'source-only candidate compilation and relocatable composition PASS',
        'source_inputs': inputs,
        'compiler_header_inputs': tool_headers,
        'binutils': {name: {'path': path, 'sha256': digest(Path(path).resolve())}
                     for name, path in [('ar', ar), ('ld', ld), ('nm', nm)]},
        'compiler': {'path': cc, 'sha256': digest(Path(cc)), 'version': run([cc, '--version'])},
        'commands': commands,
        'outputs': {p.name: digest(p) for p in [*objects, archive, combined]},
        'unresolved_link_symbols': undefined.splitlines(),
        'limits': ['Not a firmware ELF or payload; address and provider contracts remain unresolved.',
                   'Function-pointer providers do not appear in the undefined-symbol list.',
                   'No byte identity or hardware execution is established by this build.'],
    }
    (OUT / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'objects': len(objects), 'archive': str(archive),
                      'unresolved_link_symbols': undefined.splitlines()}, indent=2))


if __name__ == '__main__':
    main()
