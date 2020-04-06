# Build images
docker build --tag bs_base -f deploy/Dockerfile.bs_base .
docker build --tag bs_api -f deploy/Dockerfile.api .
docker build --tag bs_gui -f deploy/Dockerfile.gui .
docker build --tag bs_parser -f deploy/Dockerfile.parser .
docker build --tag bs_saver -f deploy/Dockerfile.saver .
docker build --tag bs_server -f deploy/Dockerfile.server .

# Kill old containers
docker container kill $(docker ps -q -f "name=bs_")

# Create docker infrastructure - virtual network and local volumes
docker network create bsnetwork
mkdir -p /tmp/brainstorm/data
mkdir -p /tmp/brainstorm/resources

# 3rd party containers - MQ and DB
docker run -d --rm --name bs_postgres_host --network=bsnetwork -p 5432:5432 -e POSTGRES_PASSWORD=1234 postgres;
docker run -d -it --rm --name bs_rabbit_host --network=bsnetwork -p 5672:5672 -p 15672:15672 rabbitmq:3-management;

# BrainStorm components
docker run --rm --name bs_server_host --network=bsnetwork -d -p 8000:8000 bs_server
docker run --rm --name bs_saver_host --network=bsnetwork -d bs_saver
docker run --rm --name bs_api_host --network=bsnetwork -d -p 5000:5000 bs_api
docker run --rm --name bs_gui_host --network=bsnetwork -d -p 8080:8080 bs_gui
# BrainStorm parsers
docker run --rm --name bs_parse_col_img_host --network=bsnetwork -d -e parser_name=color_image bs_parser
docker run --rm --name bs_parse_dep_img_host --network=bsnetwork -d -e parser_name=depth_image bs_parser
docker run --rm --name bs_parse_feel_host --network=bsnetwork -d -e parser_name=feelings bs_parser
docker run --rm --name bs_parse_pose_host --network=bsnetwork -d -e parser_name=pose bs_parser
