# AI Attendance System — Code Review Rules

1. **Preserve Functional Behavior**: Preserve existing behavior unless a verified defect exists.
2. **No Arbitrary Deletions**: Never delete code merely because it is old.
3. **Prove Unused Code**: Prove unused/dead code before removing it.
4. **Run Regression Tests**: Run tests after every logical change.
5. **No Schema Changes**: Never modify database schema during cleanup without approval.
6. **No Secret Exposure**: Never expose password hashes or personal credentials.
7. **No Biometric Vector Exposure**: Never expose biometric 128D embeddings or raw face photos.
8. **No Secret Commits**: Never commit raw face images, secrets, or temporary database files.
9. **No Model Modification**: Never modify ONNX models or retrain weights.
10. **No Threshold Modification**: Never change recognition threshold $0.363$.
11. **No Test Inflation/Deletion**: Never remove tests merely because they fail. Fix underlying issues.
12. **Root Cause Fixes**: Fix root causes rather than suppressing warnings or swallowing exceptions.
13. **Layer Separation**: Keep UI logic separate from business services and repository logic.
14. **Parameterized SQL**: Keep database access parameterized (`?`).
15. **Resource Cleanup**: Clean up OpenCV/Tkinter/Matplotlib resources cleanly.
16. **Offline First**: Preserve 100% offline, local operation.
17. **CPU First**: Preserve CPU-first performance without requiring CUDA/GPU.
18. **Packaging Safety**: Preserve PyInstaller standalone executable structure.
19. **Zero Cloud Dependencies**: Do not introduce remote cloud APIs.
