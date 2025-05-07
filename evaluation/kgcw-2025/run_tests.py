import shutil
import subprocess
import argparse
from pathlib import Path
from rdflib import Graph
from rdflib.compare import to_isomorphic
from contextlib import suppress

TYPHON_JAR = Path("./typhon-rml.jar")
TYPHON_SKELETON_JAR = Path("./chimera-typhon-skeleton.jar")
TIMEOUT_SECONDS = 10

def clean_test_cases(test_dirs):
    for folder in test_dirs:
        done_file = folder / '.done'
        with suppress(FileNotFoundError):
            done_file.unlink()
    print('Cleaned all test cases')


def run_test_case(test_path: Path, index: int, total: int, failed_tests: set):
    test_name = test_path.name
    done_file = test_path / '.done'

    if done_file.exists():
        print(f'({index}/{total}). Skipping already passed test {test_name}', flush=True)
        return

    print(f'({index}/{total}). Running test {test_name}', flush=True)

    shutil.copy(TYPHON_JAR, test_path)
    shutil.copy(TYPHON_SKELETON_JAR, test_path)

    # Folder in which generated route and template are stored
    data_dir = test_path / 'data'
    data_dir.mkdir(exist_ok=True)

    should_fail = not (test_path / 'output.nq').is_file()

    if not should_fail:
        expected_dir = test_path / 'expected'
        expected_dir.mkdir(exist_ok=True)
        # save version of the expected output
        shutil.copy(test_path / 'output.nq', expected_dir)
        Path(test_path / 'output.nq').unlink()


    try:    
        subprocess.run(["java", "-jar", "typhon-rml.jar", "--rml-mapping", "mapping.ttl"], cwd=test_path)

        route_path = test_path / 'route.xml'
        template_path = test_path / 'template.vm'
        shutil.copy(route_path, data_dir)
        shutil.copy(template_path, data_dir)

    except Exception as e:
        print(f'Failed to generate route or template for test case: {test_name}')
        print(e)        

        if should_fail:
            print(f'Test case {test_name} should fail', flush=True)
            print(f'Passed test case {test_name}', flush=True)
            done_file.touch()
            remove_dup_files(test_path)
            return

    try:
        result = subprocess.run(
            ["java", "-jar", "chimera-typhon-skeleton.jar"],
            cwd=test_path,
            check=True,
            timeout=TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        print(f'Template execution for {test_name} timed out', flush=True)
        if should_fail:
            print(f'Test case {test_name} should fail', flush=True)
            print(f'Passed test case {test_name}', flush=True)
            done_file.touch()
            remove_dup_files(test_path)
            return
        else:
            print(f'Failed test case {test_name}', flush=True)
            failed_tests.add(test_name)
            remove_dup_files(test_path)
            return

    except subprocess.CalledProcessError:
        print(f'Template execution for {test_name} failed with an error', flush=True)
        if should_fail:
            print(f'Test case {test_name} should fail', flush=True)
            print(f'Passed test case {test_name}', flush=True)
            done_file.touch()
            remove_dup_files(test_path)
            return
        else:
            print(f'Failed test case {test_name}', flush=True)
            failed_tests.add(test_name)
            remove_dup_files(test_path)
            return

    if not should_fail:
        try:
            graph_expected = Graph().parse(test_path / 'expected' / 'output.nq')
            graph_produced = Graph().parse(test_path / 'output.nq')
            if to_isomorphic(graph_expected) == to_isomorphic(graph_produced):
                print(f'Passed test case {test_name}', flush=True)
                if Path(test_path / 'typhon_output.nq').exists():
                    Path(test_path / 'typhon_output.nq').unlink()                
                Path(test_path / 'output.nq').rename(test_path / 'typhon_output.nq')
                shutil.copy(expected_dir / 'output.nq', test_path)
                done_file.touch()
            else:
                print(f'Failed test case {test_name}', flush=True)
                failed_tests.add(test_name)
            remove_dup_files(test_path)
        except Exception as e:
            print(f'Error comparing RDF for {test_name}: {e}', flush=True)
            failed_tests.add(test_name)
            remove_dup_files(test_path)

def remove_dup_files(test_path: Path):
    route_path = test_path / 'route.xml'
    template_path = test_path / 'template.vm'

    for file in [route_path, template_path,
                 test_path / 'typhon-rml.jar',
                 test_path / 'chimera-typhon-skeleton.jar',
                 test_path / 'mapping-augmented.ttl']:
        with suppress(FileNotFoundError):
            file.unlink()

def main():
    parser = argparse.ArgumentParser(description="Run RML test cases")
    parser.add_argument('--path', type=str, default=str(Path.cwd()), help='Path to the directory containing test-cases folder')
    parser.add_argument('--clean', action='store_true', help='Clean up after test runs')
    args = parser.parse_args()

    test_cases_path = Path(args.path)

    if not test_cases_path.exists():
        print(f"Error: test-cases directory not found at {test_cases_path}")
        return

    test_dirs = sorted([
        d for d in test_cases_path.iterdir()
        if d.is_dir() and d.name.startswith("RML")
    ])

    if args.clean:
        clean_test_cases(test_dirs)
        return

    failed_tests = set()

    for i, test_path in enumerate(test_dirs, start=1):
        run_test_case(test_path, i, len(test_dirs), failed_tests)

    print(f'\nFailed {len(failed_tests)}/{len(test_dirs)} tests')
    if failed_tests:
        print(f'Failures: {sorted(failed_tests)}')


if __name__ == "__main__":
    main()
