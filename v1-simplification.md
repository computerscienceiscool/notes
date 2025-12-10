Files Confirmed for Docker SDK Migration:
Primary Files (10 exec.Command("docker", ...) calls found):

pkg/sandbox/client.go - 3 calls

docker version (check Docker availability)
docker image inspect (check if image exists)
docker pull (pull image if missing)


pkg/sandbox/container.go - 1 call

docker run with all args (main container execution)


pkg/sandbox/io_container.go - 3 calls

docker run for read operations
docker run for write operations
docker image inspect (check image)



Test Files (3 calls):

pkg/sandbox/client_test.go - 1 call (check Docker)
pkg/sandbox/container_test.go - 1 call (check Docker)
pkg/sandbox/io_container_test.go - 0 calls (but needs update
