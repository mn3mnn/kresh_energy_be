#!/usr/bin/env bash
# One-time setup for the dedicated Ubuntu VPS that hosts Kresh Energy
# (backend + frontend). Safe to re-run; steps are idempotent. Run from the
# backend repo root after cloning:
#   bash scripts/setup_server.sh
#
# This VPS owns the edge: the backend compose project runs Traefik (binds
# 80/443 + Let's Encrypt), Django, Postgres and Redis; the frontend compose
# project runs only the Next.js container. Both attach to the shared external
# "kresh_web" docker network so Traefik can route energy.kresh-ng.de to the
# frontend and energy-api.kresh-ng.de to Django.

set -euo pipefail

DEPLOY_KEY="$HOME/.ssh/github_actions_deploy"

echo "==> Installing Docker Engine + Compose plugin (skipped if present)"
if ! command -v docker >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo apt-get install -y -qq ca-certificates curl gnupg

  sudo install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  sudo chmod a+r /etc/apt/keyrings/docker.gpg

  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
    https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
    | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

  sudo apt-get update -qq
  sudo apt-get install -y -qq \
    docker-ce docker-ce-cli containerd.io \
    docker-buildx-plugin docker-compose-plugin

  sudo usermod -aG docker "$USER"
fi
echo "==> Docker installed: $(docker --version)"
echo "==> Docker Compose installed: $(docker compose version)"

echo ""
echo "==> Ensuring the shared 'kresh_web' network exists (used by Traefik)"
docker network inspect kresh_web >/dev/null 2>&1 || docker network create kresh_web
echo "    kresh_web network ready"

echo ""
echo "==> Installing and configuring UFW firewall"
sudo apt-get install -y -qq ufw
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
echo "==> UFW status:"
sudo ufw status numbered

echo ""
echo "==> Generating SSH deploy key for GitHub Actions"
if [[ -f "$DEPLOY_KEY" ]]; then
  echo "    Key already exists at $DEPLOY_KEY — skipping generation"
else
  ssh-keygen -t ed25519 -C "github-actions-deploy" -f "$DEPLOY_KEY" -N ""
fi

if ! grep -qF "$(cat "$DEPLOY_KEY.pub")" "$HOME/.ssh/authorized_keys" 2>/dev/null; then
  mkdir -p "$HOME/.ssh"
  chmod 700 "$HOME/.ssh"
  cat "$DEPLOY_KEY.pub" >> "$HOME/.ssh/authorized_keys"
  chmod 600 "$HOME/.ssh/authorized_keys"
  echo "    Public key added to authorized_keys"
else
  echo "    Public key already in authorized_keys"
fi

echo ""
echo "========================================================"
echo "  SETUP COMPLETE — remaining steps"
echo "========================================================"
echo ""
echo "1. Add these secrets to BOTH GitHub repos (kresh_energy_be and"
echo "   kresh_energy_fe): Settings -> Secrets and variables -> Actions."
echo ""
echo "   PRODUCTION_HOST     = $(curl -s ifconfig.me 2>/dev/null || echo '<your VPS IP>')"
echo "   PRODUCTION_USER     = $USER"
echo "   PRODUCTION_SSH_PORT = 22"
echo "   PRODUCTION_APP_DIR  = (backend repo) $(pwd)"
echo "                         (frontend repo) <path where you clone kresh_energy_fe>"
echo "   PRODUCTION_DJANGO_ENV   = <full contents of .envs/.production/.django>   (backend only)"
echo "   PRODUCTION_POSTGRES_ENV = <full contents of .envs/.production/.postgres> (backend only)"
echo "   GHCR_PAT            = <GitHub PAT with read:packages, to pull private images>"
echo ""
echo "   PRODUCTION_SSH_KEY (copy everything below, including header/footer lines):"
echo "------------------------------------------------------------------------"
cat "$DEPLOY_KEY"
echo "------------------------------------------------------------------------"
echo ""
echo "2. DNS A records -> this VPS IP (all proxied through Cloudflare):"
echo "     energy.kresh-ng.de"
echo "     www.energy.kresh-ng.de"
echo "     energy-api.kresh-ng.de"
echo "     energy.kresh-ng.com   (redirects to energy.kresh-ng.de)"
echo "     energy.kresh-ng.org   (redirects to energy.kresh-ng.de)"
echo "   DNS CNAME for public R2 media:"
echo "     energy-media.kresh-ng.de -> <public R2 bucket domain>"
echo "   NOTE: apex domains (kresh-ng.de/.com/.org, no subdomain) are reserved"
echo "   for a separate site and are NOT part of this setup."
echo ""
echo "3. Clone the frontend repo into its own directory on this VPS."
echo ""
echo "4. Deploy backend first (Actions -> Deploy -> Run workflow), then frontend."
echo ""
echo "NOTE: Log out and back in (or run 'newgrp docker') for the docker group"
echo "      change to take effect before running docker commands manually."
