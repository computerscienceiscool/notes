Here's a concise walkthrough listing files and functions for each feature:
OPEN Command

    pkg/scanner/scanner.go → Scan() - Detects <open>, extracts filepath
    pkg/evaluator/executor.go → Execute() - Dispatches to open handler
    pkg/evaluator/open.go → ExecuteOpen() - Main handler
    pkg/sandbox/path.go → ValidatePath() - Security checks
    pkg/evaluator/open.go → Direct: os.ReadFile() OR Containerized: sandbox.ReadFileInContainer()
    pkg/sandbox/io_container.go → ReadFileInContainer() - Runs cat in container
    internal/app/app.go → scanInput() - Formats output

WRITE Command

    pkg/scanner/scanner.go → Scan() - Detects <write>, extracts filepath + content
    pkg/evaluator/executor.go → Execute() - Dispatches to write handler
    pkg/evaluator/write.go → ExecuteWrite() - Main handler
    pkg/sandbox/path.go → ValidatePath() - Path security
    pkg/sandbox/extension.go → ValidateWriteExtension() - Extension check
    pkg/evaluator/write.go → CreateBackup() - Backup if exists
    pkg/evaluator/write.go → FormatContent() - Format Go/JSON
    pkg/evaluator/write.go → Direct: os.WriteFile() OR Containerized: sandbox.WriteFileInContainer()
    pkg/sandbox/io_container.go → WriteFileInContainer() - Atomic write in container
    internal/app/app.go → scanInput() - Formats output

EXEC Command

    pkg/scanner/scanner.go → Scan() - Detects <exec>, extracts command + stdin
    pkg/evaluator/executor.go → Execute() - Dispatches to exec handler
    pkg/evaluator/exec.go → ExecuteExec() - Main handler
    pkg/sandbox/exec_validation.go → ValidateExecCommand() - Whitelist check
    pkg/sandbox/client.go → CheckDockerAvailability() - Verify Docker
    pkg/sandbox/client.go → PullDockerImage() - Ensure image exists
    pkg/sandbox/container.go → RunContainer() - Create/start/execute/cleanup
    internal/app/app.go → scanInput() - Formats output

SEARCH Command

    pkg/scanner/scanner.go → Scan() - Detects <search>, extracts query
    pkg/evaluator/executor.go → Execute() - Dispatches to search handler
    pkg/evaluator/search.go → ExecuteSearch() - Main handler
    internal/search/engine.go → NewSearchEngine() - Initialize
    internal/search/database.go → InitSearchDB() - Open SQLite
    internal/search/engine.go → Search() - Main search logic
    internal/search/engine.go → checkOllamaAvailability() - Verify Ollama
    internal/search/embedding.go → generateEmbedding() - Call Ollama API for query
    internal/search/engine.go → Query DB, loop through files
    internal/search/similarity.go → cosineSimilarity() - Calculate scores
    internal/search/results.go → rankSearchResults() - Sort by score
    pkg/evaluator/search.go → formatSearchOutput() - Format results
    internal/app/app.go → scanInput() - Output to user

