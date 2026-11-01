#!/usr/bin/env bash
# Laptop-side control of the Project D VM. Billing events are logged to vm/sessions.log.
#   vm/vmctl.sh restore   create RG, disk from the C snapshot, VM (SSH from your IP only, auto-shutdown)
#   vm/vmctl.sh start | stop (DEALLOCATE) | status | ssh | ip
#   vm/vmctl.sh push      copy D code (no data) to ~/d on the VM
#   vm/vmctl.sh fetch RUN copy ~/d/experiments/*/runs/RUN back and verify SHA256SUMS
#   vm/vmctl.sh hours     logged VM hours and compute cost
#   vm/vmctl.sh delete    delete the resource group (asks you to type its name; the snapshot is elsewhere and stays)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; D_ROOT="$(dirname "$HERE")"
source "$HERE/vm.env"
LOG="$HERE/sessions.log"; PRICE_PER_H=0.529
ip() { az vm show -d -g "$RG" -n "$VM" --query publicIps -o tsv; }
note() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $1 $SIZE" >> "$LOG"; }
case "${1:-}" in
  restore)
    MYIP=$(curl -s https://api.ipify.org)
    az group create -n "$RG" -l "$LOCATION" --tags project=D -o none
    az disk create -g "$RG" -n "${VM}-osdisk" --source "$SNAPSHOT_ID" --sku "$DISK_SKU" --size-gb "$DISK_GB" \
      --os-type Linux --hyper-v-generation V2 --tags project=D -o none
    az vm create -g "$RG" -n "$VM" --attach-os-disk "${VM}-osdisk" --os-type linux --size "$SIZE" \
      --disk-controller-type "$DISK_CONTROLLER" --public-ip-sku Standard --nsg-rule NONE \
      --assign-identity '[system]' --tags project=D -o none
    note start
    az network nsg rule create -g "$RG" --nsg-name "${VM}NSG" -n ssh-from-my-ip --priority 1000 \
      --source-address-prefixes "$MYIP/32" --destination-port-ranges 22 --protocol Tcp --access Allow -o none
    az vm auto-shutdown -g "$RG" -n "$VM" --time "$AUTO_SHUTDOWN_UTC" -o none
    echo "VM up at $(ip)" ;;
  start)  az vm start -g "$RG" -n "$VM" -o none; note start; echo "running at $(ip)" ;;
  stop)   az vm deallocate -g "$RG" -n "$VM" -o none; note stop; echo deallocated ;;
  status) az vm get-instance-view -g "$RG" -n "$VM" --query "instanceView.statuses[1].displayStatus" -o tsv; ip ;;
  ip)     ip ;;
  ssh)    shift; ssh -o ServerAliveInterval=60 -o StrictHostKeyChecking=accept-new "$ADMIN@$(ip)" "$@" ;;
  push)   rsync -az --exclude 'data/' --exclude 'runs/' --exclude 'paper/' --exclude 'lit/' --exclude 'vm/sessions.log' \
            "$D_ROOT/" "$ADMIN@$(ip):d/" ;;
  fetch)
    RUN="${2:?usage: vmctl.sh fetch RUN_ID}"; EXP="${RUN%%_*}"
    SRC=$(ssh "$ADMIN@$(ip)" "ls -d d/experiments/*/runs/$RUN" ) ; DEST="$D_ROOT/${SRC#d/}"
    [ -e "$DEST" ] && { echo "$DEST exists; never overwrite a run"; exit 1; }
    mkdir -p "$DEST"; rsync -az "$ADMIN@$(ip):$SRC/" "$DEST/"; (cd "$DEST" && sha256sum -c --quiet SHA256SUMS && echo "checksums OK") ;;
  hours)
    python3 - "$LOG" "$PRICE_PER_H" <<'PY'
import sys, datetime as dt
total, start = 0.0, None
for line in open(sys.argv[1]):
    ts, ev = line.split()[:2]; t = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if ev == "start" and start is None: start = t
    elif ev in ("stop", "delete") and start is not None: total += (t - start).total_seconds()/3600; start = None
print(f"logged VM hours {total:.2f}; compute ~${total*float(sys.argv[2]):.2f}" + (" (still running)" if start else ""))
PY
    ;;
  delete)
    read -r -p "Type $RG to delete it: " a; [ "$a" = "$RG" ] || exit 1
    az group delete -n "$RG" --yes --no-wait; note delete ;;
  *) sed -n '2,8p' "$0"; exit 1 ;;
esac
