import shutil
import subprocess
import argparse
from pathlib import Path
from rdflib import Graph
from rdflib.compare import to_isomorphic
from contextlib import suppress
import csv
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent
TYPHON_JAR = SCRIPT_DIR / "typhon-rml.jar"
SHUTDOWN_PROCESSOR_JAVA = SCRIPT_DIR / "ShutDownProcessor.java"
TIMEOUT_SECONDS = 30
DEFAULT_TEST_CASES = SCRIPT_DIR / "kg-construct-rml-core-4c5b14a" / "test-cases"

# JBang Camel command – kept as a string for safe use with shell=True on Windows
JBANG_CAMEL_CMD = (
    'jbang camel@apache/camel run'
    ' --dep=mvn:com.cefriel:camel-chimera-mapping-template:4.6.0'
)


def _find_output_file(folder: Path) -> Path | None:
    """Return the expected output file in *folder*, or None if absent.
    Supports both 'output.nq' and 'default.nq' naming conventions."""
    for name in ('output.nq', 'default.nq'):
        p = folder / name
        if p.is_file():
            return p
    return None


def clean_test_cases(test_dirs):
    for folder in test_dirs:
        # Remove .done marker
        with suppress(FileNotFoundError):
            (folder / '.done').unlink()

        # Restore expected output from the expected/ backup if it was moved aside during a run
        for name in ('output.nq', 'default.nq'):
            expected_backup = folder / 'expected' / name
            original_output = folder / name
            if expected_backup.is_file() and not original_output.is_file():
                shutil.copy(expected_backup, original_output)

        # Remove generated artefacts
        for name in ['route.xml', 'template.vm', 'mapping-augmented.ttl', 'typhon_output.nq']:
            with suppress(FileNotFoundError):
                (folder / name).unlink()

        # Remove generated subdirectories
        for subdir in ['data', 'expected', '.camel']:
            with suppress(Exception):
                shutil.rmtree(folder / subdir)

    print('Cleaned all test cases')


def should_test_fail(test_path: Path) -> bool:
    """Determine if a test is expected to produce an error by reading its README.md."""
    readme = test_path / 'README.md'
    if readme.is_file():
        content = readme.read_text(encoding='utf-8', errors='replace')
        for line in content.splitlines():
            if 'Error expected?' in line:
                return 'yes' in line.lower()
        # README exists but no "Error expected?" line found – fall back
    # Fallback: no expected output file means the test should fail
    return _find_output_file(test_path) is None


def run_test_case(test_path: Path, index: int, total: int, failed_tests: set):
    test_name = test_path.name
    done_file = test_path / '.done'

    if done_file.exists():
        print(f'({index}/{total}). Skipping already passed test {test_name}', flush=True)
        return

    print(f'({index}/{total}). Running test {test_name}', flush=True)

    # Folder in which the template is placed (referenced by route.xml as ./data/template.vm)
    data_dir = test_path / 'data'
    data_dir.mkdir(exist_ok=True)

    should_fail = should_test_fail(test_path)

    if not should_fail:
        expected_dir = test_path / 'expected'
        expected_dir.mkdir(exist_ok=True)
        # save a copy of the expected output before it gets overwritten by camel
        output_file = _find_output_file(test_path)
        shutil.copy(output_file, expected_dir)
        output_file.unlink()

    # ── Step 1: Run typhon-rml to produce route.xml + template.vm ──
    try:
        subprocess.run(
            f'java -jar "{TYPHON_JAR}" --rml-mapping mapping.ttl',
            cwd=test_path,
            check=True,
            timeout=TIMEOUT_SECONDS,
            shell=True,
        )

        route_path = test_path / 'route.xml'
        template_path = test_path / 'template.vm'

        if not route_path.exists() or not template_path.exists():
            raise FileNotFoundError("route.xml or template.vm not generated")

        # The route references the template at ./data/template.vm
        shutil.copy(template_path, data_dir)

    except Exception as e:
        print(f'  typhon-rml failed for {test_name}: {e}', flush=True)

        if should_fail:
            print(f'  Expected failure – PASSED {test_name}', flush=True)
            done_file.touch()
        else:
            print(f'  FAILED {test_name}', flush=True)
            failed_tests.add(test_name)
            _restore_expected(test_path)
        return

    # ── Step 2: Execute the Camel route via JBang ──
    try:
        subprocess.run(
            f'{JBANG_CAMEL_CMD} route.xml "{SHUTDOWN_PROCESSOR_JAVA}"',
            cwd=test_path,
            check=True,
            timeout=TIMEOUT_SECONDS,
            shell=True,
        )
    except subprocess.TimeoutExpired:
        print(f'  Camel route timed out for {test_name}', flush=True)
        if should_fail:
            print(f'  Expected failure – PASSED {test_name}', flush=True)
            done_file.touch()
            _restore_expected(test_path)
        else:
            print(f'  FAILED {test_name}', flush=True)
            failed_tests.add(test_name)
            _restore_expected(test_path)
        return

    except subprocess.CalledProcessError:
        print(f'  Camel route errored for {test_name}', flush=True)
        if should_fail:
            print(f'  Expected failure – PASSED {test_name}', flush=True)
            done_file.touch()
            _restore_expected(test_path)
        else:
            print(f'  FAILED {test_name}', flush=True)
            failed_tests.add(test_name)
            _restore_expected(test_path)
        return

    # ── Step 3: Compare produced output with expected ──
    if should_fail:
        # Route succeeded but the test was supposed to fail
        if _find_output_file(test_path) is not None:
            print(f'  Route produced output but test should fail – FAILED {test_name}', flush=True)
            failed_tests.add(test_name)
        else:
            print(f'  No output produced (expected) – PASSED {test_name}', flush=True)
            done_file.touch()
        return

    try:
        produced_path = _find_output_file(test_path)
        expected_path = _find_output_file(test_path / 'expected')

        if produced_path is None:
            print(f'  No output.nq/default.nq produced – FAILED {test_name}', flush=True)
            failed_tests.add(test_name)
            _restore_expected(test_path)
            return

        graph_expected = Graph().parse(expected_path)
        graph_produced = Graph().parse(produced_path)

        if to_isomorphic(graph_expected) == to_isomorphic(graph_produced):
            print(f'  PASSED {test_name}', flush=True)
            # Keep the produced output as typhon_output for reference
            typhon_out = test_path / 'typhon_output.nq'
            with suppress(FileNotFoundError):
                typhon_out.unlink()
            produced_path.rename(typhon_out)
            # Restore original expected output
            shutil.copy(expected_path, test_path / expected_path.name)
            done_file.touch()
        else:
            print(f'  Graph mismatch – FAILED {test_name}', flush=True)
            failed_tests.add(test_name)
            _restore_expected(test_path)
    except Exception as e:
        print(f'  Error comparing RDF for {test_name}: {e}', flush=True)
        failed_tests.add(test_name)
        _restore_expected(test_path)


def _restore_expected(test_path: Path):
    """Put the expected output file back if it was moved aside."""
    for name in ('output.nq', 'default.nq'):
        expected_path = test_path / 'expected' / name
        target_path = test_path / name
        if expected_path.is_file() and not target_path.is_file():
            shutil.copy(expected_path, target_path)



def main():
    parser = argparse.ArgumentParser(description="Run RML conformance test cases")
    parser.add_argument('--path', type=str,
                        default=str(DEFAULT_TEST_CASES),
                        help='Path to the directory containing the RMLTC* test-case folders')
    parser.add_argument('--clean', action='store_true',
                        help='Remove .done markers and generated artefacts')
    args = parser.parse_args()

    test_cases_path = Path(args.path)

    if not test_cases_path.exists():
        print(f"Error: directory not found at {test_cases_path}")
        return

    # Support running a single test when path points directly to a test folder
    single_test = test_cases_path.name.startswith("RML") and test_cases_path.is_dir() and \
                  not any(d.is_dir() and d.name.startswith("RML") for d in test_cases_path.iterdir())

    if single_test:
        test_dirs = [test_cases_path]
    else:
        test_dirs = sorted([
            d for d in test_cases_path.iterdir()
            if d.is_dir() and d.name.startswith("RML")
        ])

    if not test_dirs:
        print(f"No RMLTC* test directories found in {test_cases_path}")
        return

    if args.clean:
        clean_test_cases(test_dirs)
        return

    failed_tests = set()
    test_results = {}

    for i, test_path in enumerate(test_dirs, start=1):
        run_test_case(test_path, i, len(test_dirs), failed_tests)
        test_results[test_path.name] = test_path.name not in failed_tests

    print(f'\n{"="*60}')
    print(f'Results: {len(test_dirs) - len(failed_tests)} passed, '
          f'{len(failed_tests)} failed out of {len(test_dirs)} tests')
    if failed_tests:
        print(f'Failures: {sorted(failed_tests)}')

    # Write results to CSV file (skip for single-test runs to avoid clutter)
    if not single_test:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_suite_name = test_cases_path.parent.name
        csv_filename = f"{timestamp}_{test_suite_name}_results.csv"
        csv_path = SCRIPT_DIR / csv_filename

        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Test Name', 'Passed'])
            for test_name in sorted(test_results.keys()):
                status = 'PASSED' if test_results[test_name] else 'FAILED'
                writer.writerow([test_name, status])

        print(f'Results saved to: {csv_path}')


if __name__ == "__main__":
    main()
