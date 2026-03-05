# open-webui-tools


- Add ppa to your system

    > sudo add-apt-repository ppa:sgallet/open-webui-tools

    > sudo apt update

- Remove Docker installed by Ubuntu

    > sudo apt remove $(dpkg --get-selections docker.io docker-compose docker-compose-v2 docker-doc podman-docker containerd runc | cut -f1)

- Installs dependency sources.

    Must be installed separately before installing other packages.

    > sudo apt install open-webui-deps

- Installs main components.

    > sudo apt install open-webui

- Configure.

    Modify the Docker images and configuration settings according to your hardware and needs.

    You can edit the files open-webui-app.conf, open-webui-ollama.conf, open-webui-postgresql.conf directly
    or put your changes in open-webui-local.conf(this file has priority)

    Update your installation

    > sudo owebui update
