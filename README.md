# open-webui-tools

This tutorial will guide you through installing Open WebUI connected to a
PostgreSQL database (with the "vector" extension) and an Olama server.

He also explains how to install caddy and docling

It uses Docker images and stores data on disk in separate directories within /var/lib/owebui.


- Add ppa to your system

    > sudo add-apt-repository ppa:sgallet/open-webui-tools

    > sudo apt update

- Remove Docker installed by Ubuntu

    > sudo apt remove $(dpkg --get-selections docker.io docker-compose docker-compose-v2 docker-doc podman-docker containerd runc | cut -f1)

- Install dependency package.

    This will add the Docker and NVIDIA Container Toolkit APT sources.

    Must be installed separately before installing other packages.

    > sudo apt install open-webui-deps

- Installs main components.

    > sudo apt install open-webui

    Check status

    > sudo owebui status

        > open-webui-postgresql : activating
        > open-webui-ollama : activating
        > open-webui-app : inactive

- Configure.

    Modify the Docker images and configuration settings according to your hardware and needs.

    You can edit the files open-webui-app.conf, open-webui-ollama.conf, open-webui-postgresql.conf directly
    or put your changes in open-webui-local.conf(this file has priority and is recommended) in /etc/open-webui.

    You can define environment variable to pass to docker container by prefixing them with (service)_.
    For example, to change the logging level for the Open WebUI application, set app_GLOBAL_LOG_LEVEL=WARNING

    Environment Variable for OpenWeb UI : https://docs.openwebui.com/reference/env-configuration/

    Environment Variable for Ollama : https://ollama.com/blog/ollama-is-now-available-as-an-official-docker-image


- Update and start.

    Update your installation. Following command will download all docker images and models defined in configuration.

    > sudo owebui update --force --models --restart

        > Update POSTGRES_IMAGE for open-webui-postgresql
        > Image pgvector/pgvector:pg18-trixie not found. Download it
        > Id for pgvector/pgvector:pg18-trixie : 'sha256:cdc8b3de66a0fbffceef90077fde8845a2346034ad8f309f4022a84039fed955
        > Service open-webui-postgresql restarted after update

        > Update OLLAMA_IMAGE for open-webui-ollama
        > Image ollama/ollama not found. Download it
        > Id for ollama/ollama : 'sha256:f2de8ed54c7b02ee05e42abaa454978c76fb552a883877b37588ebb62f31e41a
        > Service open-webui-ollama restarted after update

        > Install ollama models
        > Install model llama3.2

        > Update OWEBUI_IMAGE for open-webui-app
        > Image ghcr.io/open-webui/open-webui:cuda not found. Download it
        > Id for ghcr.io/open-webui/open-webui:cuda : 'sha256:a301ed36e18a3507ec4f6edcdbff67bc7ef7a9f07824ac4c240799371dc75dfe
        > Service open-webui-app restarted after update

- That's all

    All services should be operational

    > sudo owebui status

        > open-webui-postgresql : active
        > open-webui-ollama : active
        > open-webui-app : active

   You can now connect to http://127.0.0.1:8080

- Automatic update of the docker images

    You can enable them using :

    > sudo owebui update-enable

        > Started open-webui-postgresql-update timer
        > Started open-webui-ollama-update timer
        > Started open-webui-app-update timer

    And check status using :

    > sudo owebui update-status

        > open-webui-postgresql : active (inactive) - Last run at Sun 2026-03-08 03:18:48 CET; 30s ago
        > open-webui-ollama : active (inactive) - Last run at Sun 2026-03-08 03:18:48 CET; 30s ago
        > open-webui-app : active (inactive) - Last run at Sun 2026-03-08 03:18:48 CET; 30s ago

- If you plan to connect from outside, it is recommended to use a frontend like Caddy.

    > sudo apt install open-webui-caddy

    Update the Caddyfile in /etc/open-webui. {APP_IP} and {APP_PORT} will
    be replaced with the appropriate values ​​when the service starts.

    You can find more documentation here : https://caddyserver.com/docs/caddyfile

    Download docker image and start service

    > sudo owebui update --restart caddy

    Check status

    > sudo owebui status

        > open-webui-postgresql : active
        > open-webui-ollama : active
        > open-webui-app : active
        > open-webui-caddy : active

- If you plan to do OCR, it is possible to install Docling.

    > sudo apt install open-webui-docling

    Add your langs to DOCLING_IMAGE_LANGS (check configuration file) to dowload
    image and files needed for tesseract and update your local image.
    This will create a basic DOCLING_PARAMS environment variable. You can
    define more complex defining app_DOCLING_PARAMS yourself.

    > sudo owebui update --force --restart docling

    Restart Open WebUI app

    > sudo owebui restart app

    Check status

    > sudo owebui status

        > open-webui-postgresql : active
        > open-webui-ollama : active
        > open-webui-app : active
        > open-webui-docling : active

- Customize your installation.

    You can change user/group and directories creating a /etc/default/open-webui
    before installing anything. Use the one in sources as a template

    For example :

    > /etc/default/open-webui

    # Defaults for open-webui
    OWEBUI_USER=owebui
    OWEBUI_GROUP=owebui
    OWEBUI_HOME=/home/owebui
    OWEBUI_APP=/home/owebui/app
    OWEBUI_OLLAMA=/home/owebui/ollama
    OWEBUI_CADDY=/home/owebui/caddy
    OWEBUI_POSTGRESQL=/home/owebui/postgresql
    OWEBUI_SHARE=/home/owebui/share
    OWEBUI_NAME="Open WebUI"

