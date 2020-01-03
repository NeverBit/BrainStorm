To generate the output python code run in this directory:

python -m grpc.tools.protoc -I.  cortex.proto --python_out=.

( You should make sure to install grpc.tools: pip install grpcio-tools )