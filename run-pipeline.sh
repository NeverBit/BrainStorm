sudo docker build --tag bs_base -f deploy/Dockerfile.bs_base .
sudo docker build --tag bs_server -f deploy/Dockerfile.server .


sudo docker kill postgres; sudo docker rm postgres;
sudo docker run --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=1234 -d postgres;
sudo docker kill rabbit_host; sudo docker rm rabbit_host; 
sudo docker run -d -it --rm --name rabbit_host -p 5672:5672 -p 15672:15672 rabbitmq:3-management;


sudo docker kill bs_server_inst; sudo docker rm bs_server_inst; 
sudo docker run --name bs_server_host -d -p 8000:8000 bs_server