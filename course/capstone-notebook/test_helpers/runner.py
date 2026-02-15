"""Lightweight test runner for Jupyter notebook exercises."""

import traceback
import sys


# ANSI color codes for notebook output
_GREEN = "\033[92m"
_RED = "\033[91m"
_YELLOW = "\033[93m"
_RESET = "\033[0m"
_BOLD = "\033[1m"


def run_test(test_fn):
    """Run a single test function. Prints colored PASS/FAIL result.

    Usage:
        def test_health_check():
            response = simulator.chat_completions(...)
            assert response.status_code == 200

        run_test(test_health_check)
    """
    name = test_fn.__name__
    try:
        test_fn()
        print(f"{_GREEN}{_BOLD}PASS{_RESET} {name}")
        return True
    except AssertionError as e:
        msg = str(e) if str(e) else "Assertion failed"
        print(f"{_RED}{_BOLD}FAIL{_RESET} {name}")
        print(f"     {_RED}{msg}{_RESET}")
        return False
    except Exception as e:
        print(f"{_RED}{_BOLD}ERROR{_RESET} {name}")
        print(f"     {_RED}{type(e).__name__}: {e}{_RESET}")
        return False


def run_n_times(test_fn, n=10, show_each=True):
    """Run a test function N times and report pass rate.

    Usage:
        run_n_times(test_return_policy, n=20)
        # Output: 18/20 passed (90.0%) — test_return_policy

    Returns:
        dict with keys: passed, failed, total, pass_rate, failures
    """
    name = test_fn.__name__
    passed = 0
    failed = 0
    failures = []

    for i in range(n):
        try:
            test_fn()
            passed += 1
            if show_each:
                print(f"  Run {i+1:>3}/{n}: {_GREEN}PASS{_RESET}")
        except (AssertionError, Exception) as e:
            failed += 1
            failures.append(str(e) if str(e) else "Assertion failed")
            if show_each:
                print(f"  Run {i+1:>3}/{n}: {_RED}FAIL{_RESET} — {e}")

    pass_rate = (passed / n) * 100

    # Summary line
    if pass_rate == 100:
        color = _GREEN
    elif pass_rate >= 90:
        color = _YELLOW
    else:
        color = _RED

    print(f"\n{_BOLD}{color}{passed}/{n} passed ({pass_rate:.1f}%){_RESET} — {name}")

    if failures:
        unique_failures = list(set(failures))
        print(f"  Unique failure reasons ({len(unique_failures)}):")
        for reason in unique_failures[:5]:  # Show max 5
            count = failures.count(reason)
            print(f"    [{count}x] {reason}")

    return {
        "passed": passed,
        "failed": failed,
        "total": n,
        "pass_rate": pass_rate,
        "failures": failures,
    }


def run_all_tests(*test_fns):
    """Run multiple test functions and print a summary.

    Usage:
        run_all_tests(test_health, test_auth, test_return_policy)
    """
    results = []
    print(f"{_BOLD}Running {len(test_fns)} tests...{_RESET}\n")

    for fn in test_fns:
        result = run_test(fn)
        results.append((fn.__name__, result))

    passed = sum(1 for _, r in results if r)
    failed = len(results) - passed

    print(f"\n{'='*50}")
    if failed == 0:
        print(f"{_GREEN}{_BOLD}All {passed} tests passed!{_RESET}")
    else:
        print(f"{_BOLD}{passed} passed, {_RED}{failed} failed{_RESET}")
        print(f"\nFailed tests:")
        for name, result in results:
            if not result:
                print(f"  {_RED}✗{_RESET} {name}")

    return {"passed": passed, "failed": failed, "total": len(results)}
