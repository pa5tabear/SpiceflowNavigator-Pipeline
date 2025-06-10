# Sprint 04 Plan

## 1 · Sprint Goal (≤25 words)
Fix CLI multiprocessing test failure to achieve green CI status and complete infrastructure foundation.

## 2 · Deliverables & Acceptance Criteria

• **Fix Multiprocessing Test**: Resolve `test_cli_multi_runs` AttributeError with proper function serialization
• **Green CI Pipeline**: All GitHub Actions jobs pass across Python 3.9, 3.10, 3.11 versions  
• **Test Cleanup**: Remove pytest warnings and ensure robust test execution

## 3 · Time-box & LOC Budget
30 min · ≤25 net LOC across ≤2 files

## 4 · Workflow

1. **Think**: Analyze multiprocessing serialization issue in CLI code and test structure
2. **Plan**: Choose fix strategy (refactor local function, modify test, or adjust architecture)
3. **Code**: Implement solution ensuring pickleable functions for multiprocessing
4. **Test**: Verify all tests pass locally and CI shows green status

## 5 · Self-Review Rubric

- [ ] All CI jobs show green status (primary success metric)
- [ ] `test_cli_multi_runs` passes without AttributeError
- [ ] No regression in other passing tests
- [ ] Local `make test` runs clean with minimal warnings
- [ ] Multiprocessing functionality works as intended
- [ ] Ready for next development phase with stable CI foundation

## 6 · Proposed Next Sprint
Begin multi-agent communication APIs with stable CI foundation and working test suite. 