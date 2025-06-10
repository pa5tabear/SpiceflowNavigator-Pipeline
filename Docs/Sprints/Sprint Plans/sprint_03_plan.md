# Sprint 03 Plan

## 1 · Sprint Goal (≤25 words)
Emergency CI fix: resolve common-utils dependency blocking all builds with immediate workaround solution.

## 2 · Deliverables & Acceptance Criteria

• **CI Workaround**: Remove or skip common-utils installation step to unblock pipeline immediately
• **Green Build Status**: All GitHub Actions pass with temporary dependency bypass
• **Local Development**: Ensure make install/test work without common-utils requirement

## 3 · Time-box & LOC Budget
30 min · ≤20 net LOC across ≤2 files

## 4 · Workflow

1. **Think**: Identify minimal changes to bypass common-utils dependency completely
2. **Plan**: Choose fastest workaround strategy (comment out, conditional install, or remove)
3. **Code**: Implement emergency fix in CI workflow and Makefile
4. **Test**: Verify green CI status across all Python versions

## 5 · Self-Review Rubric

- [ ] All CI jobs show green status (primary success metric)
- [ ] Local make commands work without errors
- [ ] No functional regression in existing CLI features
- [ ] Emergency fix documented with clear rollback plan
- [ ] Sprint execution actually completed (not skipped)
- [ ] Ready for future common-utils integration when available

## 6 · Proposed Next Sprint
Restore Sprint 01 momentum with multi-agent APIs now that CI foundation is stable. 