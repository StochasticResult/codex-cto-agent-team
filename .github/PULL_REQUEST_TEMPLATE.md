## Summary

<!-- Briefly describe what this pull request changes and why. -->

## Related Issue(s)

<!-- Link any related issues, e.g., Fixes #12 -->

## Verification Checklist

Please confirm you ran these checks from the repository root:

- [ ] `python -m unittest discover -s tests -v` passed
- [ ] `python scripts/validate_repo.py --verify-package` passed
- [ ] `python examples/end_to_end_demo/run_demo.py --verify` passed
- [ ] No private state, real thread/host IDs, credentials, or internal paths are included
- [ ] Documentation claims follow the six-tier evidence rules in `skills/cto-agent-team/references/host-adapters.md`
- [ ] Both `README.md` and `README.zh-CN.md` are updated if user-facing behavior changed
