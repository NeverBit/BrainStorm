sudo docker build --tag bs_base -f deploy/Dockerfile.bs_base .
sudo docker build --tag bs_server -f deploy/Dockerfile.server .
sudo docker build --tag bs_pwd -f deploy/Dockerfile.pwd .

sudo docker network create bsnetwork
mkdir /tmp/brainstorm
mkdir /tmp/brainstorm/data
mkdir /tmp/brainstorm/resources

sudo docker volume create --name data
sudo docker volume create --name resources

sudo docker kill postgres; sudo docker rm postgres;
sudo docker run --name postgres --network=bsnetwork -p 5432:5432 -e POSTGRES_PASSWORD=1234 -d postgres;
sudo docker kill rabbit_host; sudo docker rm rabbit_host; 
sudo docker run -d -it --rm --name rabbit_host --network=bsnetwork -p 5672:5672 -p 15672:15672 rabbitmq:3-management;


sudo docker kill bs_server_host; sudo docker rm bs_server_host; 
sudo docker run --name bs_server_host --network=bsnetwork -d -p 8000:8000 bs_server


sudo docker kill bs_pwd_host; sudo docker rm bs_pwd_host; 
sudo docker run --name bs_pwd_host -v /tmp/brainstorm/data:/tmp/brainstorm/data --network=bsnetwork bs_pwd