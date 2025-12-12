# TODO: Remove `internal/` Package - Use Go Capitalization

## Overview
Move all `internal/` packages to `pkg/` and use Go's capitalization rules (Capital = exported, lowercase = unexported) for visibility control.

---

## 1. Move `internal/cli/` → `pkg/cli/`

### 1.1 Move files
- [ ] `git mv internal/cli pkg/cli`
- [ ] Update package declaration in all files: `package cli`

### 1.2 Unexport private functions/types
- [ ] `pkg/cli/config.go`: Rename `initConfig()` → `initConfig()` (already private)
- [ ] `pkg/cli/config.go`: Rename `buildConfig()` → `buildConfig()` (already private)
- [ ] `pkg/cli/config.go`: Rename `bootstrapApp()` → `bootstrapApp()` (already private)

### 1.3 Keep public exports
- [ ] `pkg/cli/root.go`: Keep `Execute()` exported (called by main.go)

### 1.4 Update imports
- [ ] `cmd/llm-runtime/main.go`: Change import from `internal/cli` → `pkg/cli`

---

## 2. Move `internal/app/` → `pkg/app/`

### 2.1 Move files
- [ ] `git mv internal/app pkg/app`
- [ ] Update package declaration: `package app`

### 2.2 Unexport private functions/types
- [ ] `pkg/app/app.go`: Rename `scanInput()` → `scanInput()`
- [ ] `pkg/app/app.go`: Rename `printVerboseInfo()` → `printVerboseInfo()`
- [ ] Keep `Run()`, `GetSession()`, `GetExecutor()`, `GetConfig()` exported

### 2.3 Keep public exports
- [ ] `pkg/app/bootstrap.go`: Keep `Bootstrap()` exported

### 2.4 Update imports
- [ ] `pkg/cli/config.go`: Change `internal/app` → `pkg/app`
- [ ] `pkg/cli/root.go`: Change `internal/app` → `pkg/app`

---

## 3. Move `internal/config/` → `pkg/config/`

### 3.1 Move files
- [ ] `git mv internal/config pkg/config`
- [ ] Update package declaration: `package config`

### 3.2 Review exports (most already correct)
- [ ] `pkg/config/types.go`: Keep `Config`, `FullConfig` exported
- [ ] `pkg/config/defaults.go`: Keep `SetViperDefaults()`, `LoadSearchConfig()` exported
- [ ] `pkg/config/defaults.go`: Rename `GetDefaultSearchConfig()` → `getDefaultSearchConfig()` (helper)

### 3.3 Update imports
- [ ] `pkg/app/bootstrap.go`: Change `internal/config` → `pkg/config`
- [ ] `pkg/cli/config.go`: Change `internal/config` → `pkg/config`
- [ ] `pkg/evaluator/*.go`: Change `internal/config` → `pkg/config`

---

## 4. Move `internal/session/` → `pkg/session/`

### 4.1 Move files
- [ ] `git mv internal/session pkg/session`
- [ ] Update package declaration: `package session`

### 4.2 Review exports
- [ ] `pkg/session/session.go`: Keep `Session`, `NewSession()`, `LogAudit()` exported

### 4.3 Update imports
- [ ] `pkg/app/bootstrap.go`: Change `internal/session` → `pkg/session`

---

## 5. Move `internal/search/` → `pkg/search/`

### 5.1 Move files
- [ ] `git mv internal/search pkg/search`
- [ ] Update package declaration: `package search`

### 5.2 Unexport internal helpers
- [ ] `pkg/search/database.go`: Rename `getFileInfo()` → `getFileInfo()`
- [ ] `pkg/search/database.go`: Rename `storeFileInfo()` → `storeFileInfo()`
- [ ] `pkg/search/database.go`: Rename `removeFileInfo()` → `removeFileInfo()`
- [ ] `pkg/search/database.go`: Rename `getAllIndexedFiles()` → `getAllIndexedFiles()`
- [ ] `pkg/search/database.go`: Rename `getIndexStats()` → `getIndexStats()`
- [ ] `pkg/search/embedding.go`: Rename `generateEmbedding()` → `generateEmbedding()`
- [ ] `pkg/search/embedding.go`: Rename `truncateText()` → `truncateText()`
- [ ] `pkg/search/indexing.go`: Rename `shouldIndexFile()` → `shouldIndexFile()`
- [ ] `pkg/search/indexing.go`: Rename `fileNeedsIndexing()` → `fileNeedsIndexing()`
- [ ] `pkg/search/indexing.go`: Rename `indexFile()` → `indexFile()`
- [ ] `pkg/search/indexing.go`: Rename `printIndexStats()` → `printIndexStats()`
- [ ] `pkg/search/indexing.go`: Rename `isTextFile()` → `isTextFile()`
- [ ] `pkg/search/similarity.go`: Rename `cosineSimilarity()` → `cosineSimilarity()`
- [ ] `pkg/search/similarity.go`: Rename `serializeEmbedding()` → `serializeEmbedding()`
- [ ] `pkg/search/similarity.go`: Rename `deserializeEmbedding()` → `deserializeEmbedding()`
- [ ] `pkg/search/results.go`: Rename `formatFileSize()` → `formatFileSize()`
- [ ] `pkg/search/results.go`: Rename `rankSearchResults()` → `rankSearchResults()`
- [ ] `pkg/search/results.go`: Rename `countLines()` → `countLines()`
- [ ] `pkg/search/results.go`: Rename `generatePreview()` → `generatePreview()`

### 5.3 Keep public exports
- [ ] Keep exported: `SearchEngine`, `SearchConfig`, `SearchResult`, `SearchCommands`
- [ ] Keep exported: `NewSearchEngine()`, `NewSearchCommands()`, `InitSearchDB()`
- [ ] Keep exported: `IndexRepository()`, `UpdateIndex()`, `CleanupIndex()`, `ValidateIndex()`
- [ ] Keep exported: `FormatSearchResults()`, `GetRelevanceLabel()`
- [ ] Keep exported: `CheckOllamaSetup()`

### 5.4 Update imports
- [ ] `pkg/app/bootstrap.go`: Change `internal/search` → `pkg/search`
- [ ] `pkg/config/defaults.go`: Change `internal/search` → `pkg/search`
- [ ] `pkg/evaluator/search.go`: Change `internal/search` → `pkg/search`
- [ ] `pkg/cli/commands.go`: Change `internal/search` → `pkg/search`

---

## 6. Update All Cross-Package Imports

### 6.1 Search and replace in all files
- [ ] `grep -r "internal/cli" .` → replace with `pkg/cli`
- [ ] `grep -r "internal/app" .` → replace with `pkg/app`
- [ ] `grep -r "internal/config" .` → replace with `pkg/config`
- [ ] `grep -r "internal/session" .` → replace with `pkg/session`
- [ ] `grep -r "internal/search" .` → replace with `pkg/search`

### 6.2 Update go.mod if needed
- [ ] Run `go mod tidy`

---

## 7. Final Cleanup

### 7.1 Remove internal directory
- [ ] Verify `internal/` is empty
- [ ] `rm -rf internal/`

### 7.2 Update documentation
- [ ] `llm-runtime-walkthrough.md`: Update all `internal/` references → `pkg/`
- [ ] `llm-runtime-architecture.md`: Update package structure diagram
- [ ] Update README.md if it mentions package structure

---

## 8. Verification

### 8.1 Build and test
- [ ] `go build ./...` (verify all packages compile)
- [ ] `make build`
- [ ] `make test`

### 8.2 Verify visibility
- [ ] Try importing unexported function from another package (should fail)
- [ ] Verify exported functions still accessible

---

## Result

**Before:**
```
internal/
  cli/
  app/
  config/
  session/
  search/
pkg/
  evaluator/
  scanner/
  sandbox/
```

**After:**
```
pkg/
  cli/
  app/
  config/
  session/
  search/
  evaluator/
  scanner/
  sandbox/
```

All visibility controlled by capitalization, no special `internal/` directory needed.

---

## Notes

- This is a refactoring task - no functional changes
- All tests should pass after completion
- External behavior remains identical
- Only package structure and import paths change
