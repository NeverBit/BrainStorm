sudo docker build --tag bs_base -f deploy/Dockerfile.bs_base .
sudo docker build --tag bs_server -f deploy/Dockerfile.server .

sudo docker run --name bs_server_inst -p 8000:8000 bs_server