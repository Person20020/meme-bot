#!/bin/bash

red="\033[1;31m"
yellow="\033[1;33m"
green="\033[1;32m"
reset="\033[0m"

[ "$(basename "$PWD")" != "meme-bot" ] && echo -e "${red}Please run this script from the root of the meme-bot directory after cloning the repository.${reset}" && exit 1

echo -e "${green}Creating database...${reset}"
sqlite3 ./database.db "CREATE TABLE IF NOT EXISTS responses (id INTEGER PRIMARY KEY, keyword TEXT, response TEXT, created_by TEXT);"
echo -e "${green}Database initialized.${reset}"


echo -e "${green}Setting up virtual environment...${reset}"
if [ -d "venv" ]; then
    echo -e "${yellow}Virtual environment already exists. Skipping creation.${reset}"
else
    echo -e "${green}Creating virtual environment...${reset}"
    python -m venv venv
fi
. venv/bin/activate
echo -e "${green}Installing dependencies...${reset}"
if ! pip install -r requirements.txt; then
    echo -e "${red}Failed to install dependencies from requirements.txt. You can try to install them manually.${reset}"
fi

if [ -d logs ]; then
    echo -e "${yellow}logs directory already exists. Skipping creation.${reset}"
else
    echo -e "${green}Creating logs directory...${reset}"
    mkdir logs
fi

if [ -f app/.env ]; then
    echo -e "${yellow}app/.env already exists. Skipping creation.${reset}"
else
    echo -e "${green}Creating .env file...${reset}"
    touch app/.env
fi

cat > app/.env <<EOF
# Edit this file to set your environment variables
SLACK_BOT_TOKEN=
SLACK_SIGNING_SECRET=
DB_PATH=$PWD/database.db
EOF

echo -e "${yellow}.env file created. Please edit the .env file to set your environment variables.\nYou must add your Slack API tokens and database path.${reset}"

echo -e "${green}Setup complete.${reset}"
