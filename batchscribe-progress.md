The two must-fix-before-submission items:
- 347-store-purchase-missing-initializewithwindow (critical) — StoreContext never gets InitializeWithWindow, so RequestPurchaseAsync fails in the packaged app (typically Status=Error / ERROR_INVALID_WINDOW_HANDLE, mapped to a generic purchase error). Entry includes the exact fix (lazy InitializeWithWindow.Initialize(_context, App.MainWindowHandle) before the first purchase call).
- 346-diarization-models-never-downloaded (blocker) — the two sherpa-onnx models exist only because you hand-placed them on this machine; no code path downloads or bundles them, so speaker labels throw FileNotFoundException for every Store install.

The compliance cluster:
- 369-ffmpeg-lgpl-version-and-substitution-claims-wrong — notices say LGPL v2.1, bundled build is v3; substitution/source-offer claims don't hold under MSIX.
- 361-notices-missing-ai-model-and-onnxruntime-licenses — Whisper GGML weights, pyannote segmentation-3.0, 3D-Speaker embedding, and onnxruntime.dll all absent from THIRD_PARTY_NOTICES.
- 360-privacy-policy-omits-microphone-and-recordings — policy never mentions mic/system-audio capture or the recordings folder despite the declared capability.
- 368-arm64-declared-but-native-deps-x64-only — ARM64 in the manifest, but every native dependency ships x64-only.

One gap your message exposed: the "must verify in an actual packaged MSIX run" caveat was only written into 347's entry, not 346's, and the manual QA checklist had no packaged-build steps at all. I've fixed that and pushed (af26e8d):

- Checklist §17 (new) in TODO/131-manual-qa-checklist.md: install the MSIX on a profile without hand-placed models, verify diarization-model provisioning end-to-end, verify the Store purchase dialog actually renders (cancel it — no real purchase needed), plus Whisper-download-under-package-identity and the mic consent prompt.
- 346's entry now states the packaged-run requirement explicitly.
- Drive-by: the checklist still walked QA through the DevForcePro toggle that 249 deleted — sections 4/14a/14b now use the 7-day trial as the Pro test path, and 14b became a "no trace remains" verification (including that a hand-planted devForcePro: true in settings.json unlocks nothing).
