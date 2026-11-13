#!/bin/sh
# Instala o timer diário (06:20) do nivel-ia no seu usuário (systemd --user). Desfazer: systemctl --user disable --now nivel-ia.timer
set -e
RAIZ=$(cd "$(dirname "$0")/.." && pwd)
D="$HOME/.config/systemd/user"; mkdir -p "$D"
sed "s#@RAIZ@#$RAIZ#g" "$RAIZ/systemd/nivel-ia.service" > "$D/nivel-ia.service"
cp "$RAIZ/systemd/nivel-ia.timer" "$D/nivel-ia.timer"
systemctl --user daemon-reload
systemctl --user enable --now nivel-ia.timer
echo "Instalado. Próxima rodada: $(systemctl --user list-timers nivel-ia.timer --no-legend | awk '{print $1, $2, $3}')"
