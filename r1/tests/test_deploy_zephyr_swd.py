from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
SPEC = importlib.util.spec_from_file_location(
    "deploy_zephyr_swd", TOOLS / "deploy_zephyr_swd.py")
assert SPEC is not None and SPEC.loader is not None
swd = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(swd)


class FakeTarget:
    def __init__(self, flash: bytes, uicr: bytes) -> None:
        self.flash = bytearray(flash)
        self.uicr = bytearray(uicr)
        self.halt_count = 0
        self.reset_count = 0
        self.part = swd.NRF52840_PART

    def halt(self) -> None:
        self.halt_count += 1

    def reset(self) -> None:
        self.reset_count += 1

    def read_memory(self, address: int, width: int) -> int:
        if address != swd.FICR_PART_ADDRESS or width != 32:
            raise AssertionError("unexpected scalar read")
        return self.part

    def read_memory_block8(self, address: int, length: int) -> list[int]:
        if address == 0 and length == swd.FLASH_LIMIT:
            return list(self.flash)
        if address == swd.UICR_START and length == swd.UICR_SIZE:
            return list(self.uicr)
        raise AssertionError("unexpected block read")


class FakeSession:
    def __init__(self, target: FakeTarget) -> None:
        self.target = target


class FakeNvmcTarget:
    def __init__(self) -> None:
        self.flash = bytearray(b"\x00" * swd.FLASH_LIMIT)
        self.uicr = bytearray(b"\x00" * swd.UICR_SIZE)
        self.config = swd.NVMC_CONFIG_READ
        self.config_writes: list[int] = []
        self.erase_pages: list[int] = []
        self.flash_word_writes: list[tuple[int, int]] = []
        self.register_writes: list[tuple[int, int]] = []

    def read32(self, address: int) -> int:
        if address != swd.NVMC_READY:
            raise AssertionError("unexpected NVMC read")
        return 1

    def write32(self, address: int, value: int) -> None:
        self.register_writes.append((address, value))
        if address == swd.NVMC_CONFIG:
            self.config = value
            self.config_writes.append(value)
        elif address == swd.NVMC_ERASEPAGE:
            if self.config != swd.NVMC_CONFIG_ERASE:
                raise AssertionError("erase outside erase mode")
            self.erase_pages.append(value)
            self.flash[value:value + swd.FLASH_PAGE_SIZE] = \
                b"\xff" * swd.FLASH_PAGE_SIZE
        elif address == swd.NVMC_ERASEUICR:
            if self.config != swd.NVMC_CONFIG_ERASE or value != 1:
                raise AssertionError("UICR erase outside erase mode")
            self.uicr[:] = b"\xff" * swd.UICR_SIZE
        elif swd.UICR_START <= address < swd.UICR_START + swd.UICR_SIZE:
            if self.config != swd.NVMC_CONFIG_WRITE:
                raise AssertionError("UICR write outside write mode")
            offset = address - swd.UICR_START
            self.uicr[offset:offset + 4] = value.to_bytes(4, "little")
        elif 0 <= address < swd.FLASH_LIMIT:
            if self.config != swd.NVMC_CONFIG_WRITE:
                raise AssertionError("flash write outside write mode")
            self.flash_word_writes.append((address, value))
            self.flash[address:address + 4] = value.to_bytes(4, "little")
        else:
            raise AssertionError("unexpected NVMC write")

    def read_memory_block8(self, address: int, length: int) -> list[int]:
        if address == swd.UICR_START and length == swd.UICR_SIZE:
            return list(self.uicr)
        raise AssertionError("unexpected NVMC block read")


class SwdDeploymentTests(unittest.TestCase):
    def fixture(self):
        backup = bytes(
            (index * 17 + 3) & 0xFF for index in range(swd.FLASH_LIMIT))
        uicr = bytes(
            (index * 29 + 7) & 0xFF for index in range(swd.UICR_SIZE))
        install = {
            0: 0x11,
            1: 0x22,
            0x27000: 0x33,
            swd.DATA_START - 1: 0x44,
        }
        chunks = swd.contiguous_chunks(install)
        plan = {
            "installation": {
                "erase_ranges": [
                    [0, swd.DATA_START],
                    [swd.DATA_LIMIT, swd.FLASH_LIMIT],
                ],
                "write_ranges": swd.chunk_ranges(chunks),
                "mass_erase_forbidden": True,
                "readback_required": True,
                "reset_held_until_readback_verified": True,
            },
            "recovery": {
                "requires_authorized_debug_access": True,
                "readback_range": [0, swd.FLASH_LIMIT],
                "covers_internal_flash": [0, swd.FLASH_LIMIT],
                "covers_uicr": [swd.UICR_START,
                                swd.UICR_START + swd.UICR_SIZE],
                "uicr_readback_required": True,
                "includes_uicr": False,
                "uicr_erase_before_restore_required": True,
                "expected_readback_sha256": swd.digest(backup),
                "expected_uicr_readback_sha256": swd.digest(uicr),
            },
        }
        expected = bytearray(backup)
        expected[0:swd.DATA_START] = b"\xff" * swd.DATA_START
        expected[swd.DATA_LIMIT:swd.FLASH_LIMIT] = \
            b"\xff" * (swd.FLASH_LIMIT - swd.DATA_LIMIT)
        for address, value in install.items():
            expected[address] = value
        plan["expected_readback"] = {"sha256": swd.digest(bytes(expected))}
        target = FakeTarget(backup, uicr)
        session = FakeSession(target)
        erase_calls: list[list[tuple[int, int]]] = []

        def erase(_session, ranges):
            erase_calls.append(list(ranges))
            for start, limit in ranges:
                target.flash[start:limit] = b"\xff" * (limit - start)

        def program(_session, program_chunks):
            for address, body in program_chunks:
                target.flash[address:address + len(body)] = body

        return (
            plan, install, backup, uicr, bytes(expected), target, session,
            erase_calls, erase, program)

    def test_exact_install_reads_back_before_optional_release(self) -> None:
        fixture = self.fixture()
        (plan, install, backup, uicr, expected, target, session,
         erase_calls, erase, program) = fixture
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "evidence"
            result = swd.execute_session(
                session, plan, install, backup, uicr, expected, output,
                erase, program, release_after_verify=True)
            self.assertEqual(erase_calls, [[
                (0, swd.DATA_START),
                (swd.DATA_LIMIT, swd.FLASH_LIMIT),
            ]])
            self.assertEqual(target.reset_count, 1)
            self.assertTrue(result["released_after_verification"])
            self.assertFalse(result["mass_erase_used"])
            self.assertFalse(result["uicr_written"])
            self.assertEqual(
                (output / swd.POST_FLASH_ARTIFACT).read_bytes(), expected)
            self.assertEqual(
                (output / swd.POST_UICR_ARTIFACT).read_bytes(), uicr)

    def test_preinstall_mismatch_aborts_before_erase(self) -> None:
        fixture = self.fixture()
        (plan, install, backup, uicr, expected, target, session,
         erase_calls, erase, program) = fixture
        target.flash[0x4000] ^= 1
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "evidence"
            with self.assertRaisesRegex(ValueError, "pre-install internal flash"):
                swd.execute_session(
                    session, plan, install, backup, uicr, expected, output,
                    erase, program)
            self.assertEqual(erase_calls, [])
            self.assertEqual(target.reset_count, 0)
            self.assertGreaterEqual(target.halt_count, 2)
            self.assertTrue((output / swd.PRE_FLASH_ARTIFACT).is_file())

    def test_postinstall_flash_mismatch_never_resets(self) -> None:
        fixture = self.fixture()
        (plan, install, backup, uicr, expected, target, session,
         erase_calls, erase, program) = fixture

        def corrupting_program(active_session, chunks):
            program(active_session, chunks)
            target.flash[0x1234] ^= 1

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "post-install internal flash"):
                swd.execute_session(
                    session, plan, install, backup, uicr, expected,
                    Path(directory) / "evidence", erase, corrupting_program,
                    release_after_verify=True)
            self.assertEqual(len(erase_calls), 1)
            self.assertEqual(target.reset_count, 0)
            self.assertGreaterEqual(target.halt_count, 3)

    def test_uicr_mutation_never_resets(self) -> None:
        fixture = self.fixture()
        (plan, install, backup, uicr, expected, target, session,
         _erase_calls, erase, program) = fixture

        def uicr_mutating_program(active_session, chunks):
            program(active_session, chunks)
            target.uicr[17] ^= 1

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "post-install UICR"):
                swd.execute_session(
                    session, plan, install, backup, uicr, expected,
                    Path(directory) / "evidence", erase,
                    uicr_mutating_program, release_after_verify=True)
            self.assertEqual(target.reset_count, 0)

    def test_contract_rejects_mass_erase_or_range_drift(self) -> None:
        plan, install, *_rest = self.fixture()
        plan["installation"]["mass_erase_forbidden"] = False
        with self.assertRaisesRegex(ValueError, "forbid mass erase"):
            swd.validate_execution_contract(plan, install)
        plan["installation"]["mass_erase_forbidden"] = True
        plan["installation"]["erase_ranges"][0][1] -= 0x1000
        with self.assertRaisesRegex(ValueError, "exact bounded plan"):
            swd.validate_execution_contract(plan, install)

    def test_wrong_part_and_existing_output_fail_before_mutation(self) -> None:
        fixture = self.fixture()
        (plan, install, backup, uicr, expected, target, session,
         erase_calls, erase, program) = fixture
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "evidence"
            output.mkdir()
            with self.assertRaisesRegex(ValueError, "already exists"):
                swd.execute_session(
                    session, plan, install, backup, uicr, expected, output,
                    erase, program)
            target.part = 0x12345678
            with self.assertRaisesRegex(ValueError, "not nRF52840"):
                swd.execute_session(
                    session, plan, install, backup, uicr, expected,
                    Path(directory) / "new-evidence", erase, program)
            self.assertEqual(erase_calls, [])
            self.assertEqual(target.reset_count, 0)

    def test_transparent_nvmc_backend_uses_only_page_erase_and_words(self) -> None:
        target = FakeNvmcTarget()
        session = FakeSession(target)
        swd.nvmc_sector_erase(session, [(0x1000, 0x3000)])
        self.assertEqual(target.erase_pages, [0x1000, 0x2000])
        self.assertEqual(
            target.config_writes,
            [swd.NVMC_CONFIG_ERASE, swd.NVMC_CONFIG_READ])
        swd.nvmc_program(session, [(0x1001, b"\x12\x34\x56\x78\x9a")])
        self.assertEqual(target.flash[0x1000:0x1008],
                         b"\xff\x12\x34\x56\x78\x9a\xff\xff")
        self.assertEqual(
            target.config_writes[-2:],
            [swd.NVMC_CONFIG_WRITE, swd.NVMC_CONFIG_READ])
        forbidden = {0x4001E50C, 0x4001E514}  # ERASEALL and ERASEUICR.
        self.assertFalse(any(
            address in forbidden for address, _ in target.register_writes))

    def test_exact_recovery_restores_backup_before_optional_release(self) -> None:
        fixture = self.fixture()
        (plan, _install, backup, uicr, expected, target, session,
         erase_calls, erase, program) = fixture
        target.flash[:] = expected
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "recovery-evidence"
            verifier_calls = []

            def verify_before_release(flash_path, uicr_path):
                self.assertEqual(target.reset_count, 0)
                self.assertEqual(flash_path.read_bytes(), backup)
                self.assertEqual(uicr_path.read_bytes(), uicr)
                verifier_calls.append((flash_path, uicr_path))

            result = swd.execute_recovery_session(
                session, plan, expected, backup, uicr, output, erase, program,
                release_after_verify=True,
                verification_callback=verify_before_release)
            self.assertEqual(erase_calls, [[(0, swd.FLASH_LIMIT)]])
            self.assertEqual(target.reset_count, 1)
            self.assertEqual(target.flash, backup)
            self.assertFalse(result["mass_erase_used"])
            self.assertFalse(result["uicr_written"])
            self.assertEqual(len(verifier_calls), 1)
            self.assertEqual(
                (output / swd.POST_RECOVERY_FLASH_ARTIFACT).read_bytes(),
                backup)

    def test_stale_recovery_source_aborts_before_erase(self) -> None:
        fixture = self.fixture()
        (plan, _install, backup, uicr, expected, target, session,
         erase_calls, erase, program) = fixture
        target.flash[:] = expected
        target.flash[0x7000] ^= 1
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError,
                                        "pre-recovery installed flash"):
                swd.execute_recovery_session(
                    session, plan, expected, backup, uicr,
                    Path(directory) / "evidence", erase, program,
                    release_after_verify=True)
            self.assertEqual(erase_calls, [])
            self.assertEqual(target.reset_count, 0)

    def test_recovery_uicr_drift_aborts_before_erase(self) -> None:
        fixture = self.fixture()
        (plan, _install, backup, uicr, expected, target, session,
         erase_calls, erase, program) = fixture
        target.flash[:] = expected
        target.uicr[5] ^= 1
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "pre-recovery UICR"):
                swd.execute_recovery_session(
                    session, plan, expected, backup, uicr,
                    Path(directory) / "evidence", erase, program)
            self.assertEqual(erase_calls, [])
            self.assertEqual(target.reset_count, 0)

    def test_corrupt_recovery_never_resets(self) -> None:
        fixture = self.fixture()
        (plan, _install, backup, uicr, expected, target, session,
         _erase_calls, erase, program) = fixture
        target.flash[:] = expected

        def corrupting_program(active_session, chunks):
            program(active_session, chunks)
            target.flash[0x8000] ^= 1

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError,
                                        "post-recovery internal flash"):
                swd.execute_recovery_session(
                    session, plan, expected, backup, uicr,
                    Path(directory) / "evidence", erase,
                    corrupting_program, release_after_verify=True)
            self.assertEqual(target.reset_count, 0)
            self.assertGreaterEqual(target.halt_count, 3)

    def test_recovery_contract_hash_drift_fails_closed(self) -> None:
        plan, _install, backup, uicr, expected, *_rest = self.fixture()
        plan["recovery"]["expected_readback_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "recovery hashes differ"):
            swd.validate_recovery_contract(plan, backup, uicr, expected)

    def test_uicr_disaster_restore_uses_only_explicit_uicr_erase(self) -> None:
        target = FakeNvmcTarget()
        session = FakeSession(target)
        backup = bytearray(b"\xff" * swd.UICR_SIZE)
        backup[0x14:0x18] = (0x000F8000).to_bytes(4, "little")
        backup[0x18:0x1C] = (0x000FE000).to_bytes(4, "little")
        backup[0x20C:0x210] = (0xFFFFFFFE).to_bytes(4, "little")
        swd.nvmc_restore_uicr(session, bytes(backup))
        self.assertEqual(target.uicr, backup)
        addresses = [address for address, _ in target.register_writes]
        self.assertEqual(addresses.count(swd.NVMC_ERASEUICR), 1)
        self.assertNotIn(0x4001E50C, addresses)  # ERASEALL

    def test_uicr_restore_requires_exact_separate_confirmation(self) -> None:
        _plan, _install, _backup, uicr, _expected, *_rest = self.fixture()
        with self.assertRaisesRegex(ValueError, "exact backup SHA-256"):
            swd.validate_uicr_confirmation(True, None, uicr)
        with self.assertRaisesRegex(ValueError, "exact backup SHA-256"):
            swd.validate_uicr_confirmation(True, "0" * 64, uicr)
        swd.validate_uicr_confirmation(True, swd.digest(uicr), uicr)
        swd.validate_uicr_confirmation(False, None, uicr)

    def test_disaster_recovery_restores_drifted_uicr_before_release(self) -> None:
        fixture = self.fixture()
        (plan, _install, backup, uicr, expected, target, session,
         _erase_calls, erase, program) = fixture
        target.flash[:] = expected
        target.uicr[0x20C] ^= 1

        def restore(_session, body):
            target.uicr[:] = body

        with tempfile.TemporaryDirectory() as directory:
            result = swd.execute_recovery_session(
                session, plan, expected, backup, uicr,
                Path(directory) / "evidence", erase, program,
                release_after_verify=True, restore_uicr=True,
                uicr_restore_callback=restore)
            self.assertTrue(result["uicr_written"])
            self.assertEqual(target.uicr, uicr)
            self.assertEqual(target.reset_count, 1)

    def test_corrupt_uicr_disaster_restore_never_resets(self) -> None:
        fixture = self.fixture()
        (plan, _install, backup, uicr, expected, target, session,
         _erase_calls, erase, program) = fixture
        target.flash[:] = expected
        target.uicr[3] ^= 1

        def corrupt_restore(_session, body):
            target.uicr[:] = body
            target.uicr[11] ^= 1

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "post-recovery UICR"):
                swd.execute_recovery_session(
                    session, plan, expected, backup, uicr,
                    Path(directory) / "evidence", erase, program,
                    release_after_verify=True, restore_uicr=True,
                    uicr_restore_callback=corrupt_restore)
            self.assertEqual(target.reset_count, 0)


if __name__ == "__main__":
    unittest.main()
