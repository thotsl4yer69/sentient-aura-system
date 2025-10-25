# Production Deployment Guide

Complete guide for deploying Enhanced Sentient Core as a production service on Raspberry Pi 5.

## Table of Contents
- [System Service Setup](#system-service-setup)
- [Auto-Start Configuration](#auto-start-configuration)
- [Monitoring](#monitoring)
- [Log Management](#log-management)
- [Backup and Recovery](#backup-and-recovery)
- [Performance Tuning](#performance-tuning)

---

## System Service Setup

### Create systemd Service File

```bash
sudo tee /etc/systemd/system/sentient-core.service << 'EOF'
[Unit]
Description=Enhanced Sentient Core - AI Multi-Sensor Fusion System
After=network.target multi-user.target
Wants=network.target

[Service]
Type=simple
User=mz1312
Group=mz1312
WorkingDirectory=/home/mz1312/Sentient-Core-v4

# Environment
Environment="PYENV_ROOT=/home/mz1312/.pyenv"
Environment="PATH=/home/mz1312/.pyenv/versions/coral-py39/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Launch command
ExecStart=/home/mz1312/Sentient-Core-v4/launch_enhanced.sh --no-voice-input --no-voice-output

# Restart policy
Restart=always
RestartSec=10
StartLimitInterval=200
StartLimitBurst=5

# Resource limits
MemoryLimit=2G
CPUQuota=200%

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=sentient-core

[Install]
WantedBy=multi-user.target
EOF
```

### Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable sentient-core.service

# Start service
sudo systemctl start sentient-core.service

# Check status
sudo systemctl status sentient-core.service
```

### Verify Service is Running

```bash
# Check service status
systemctl is-active sentient-core.service
# Expected: active

# View recent logs
sudo journalctl -u sentient-core.service -n 50 --no-pager

# Follow logs in real-time
sudo journalctl -u sentient-core.service -f
```

---

## Auto-Start Configuration

### Service Management Commands

```bash
# Start service
sudo systemctl start sentient-core.service

# Stop service
sudo systemctl stop sentient-core.service

# Restart service
sudo systemctl restart sentient-core.service

# Reload configuration (without restart)
sudo systemctl reload sentient-core.service

# Enable auto-start on boot
sudo systemctl enable sentient-core.service

# Disable auto-start
sudo systemctl disable sentient-core.service

# View status
sudo systemctl status sentient-core.service
```

### Boot Sequence Verification

```bash
# List all enabled services
systemctl list-unit-files --state=enabled | grep sentient

# Check boot time
systemd-analyze

# Show service startup time
systemd-analyze blame | grep sentient
```

---

## Monitoring

### Health Check Script

Create a health check script:

```bash
cat > ~/Sentient-Core-v4/scripts/health_check.sh << 'EOF'
#!/bin/bash
#
# Sentient Core Health Check
# Returns 0 if healthy, non-zero if issues detected
#

set -e

# Check if service is running
if ! systemctl is-active --quiet sentient-core.service; then
    echo "ERROR: sentient-core.service is not running"
    exit 1
fi

# Check if WebSocket port is listening
if ! ss -tlnp | grep -q ":8765"; then
    echo "ERROR: WebSocket server not listening on port 8765"
    exit 2
fi

# Check if Coral TPU is detected
if ! lsusb | grep -q "18d1:9302"; then
    echo "WARNING: Coral USB Accelerator not detected"
    # Not critical - might run in CPU fallback mode
fi

# Check memory usage
MEM_PERCENT=$(free | grep Mem | awk '{printf "%.0f", ($3/$2)*100}')
if [ "$MEM_PERCENT" -gt 90 ]; then
    echo "WARNING: High memory usage: ${MEM_PERCENT}%"
fi

# Check CPU temperature
TEMP=$(vcgencmd measure_temp | egrep -o '[0-9.]+')
TEMP_INT=${TEMP%.*}
if [ "$TEMP_INT" -gt 80 ]; then
    echo "WARNING: High CPU temperature: ${TEMP}°C"
fi

echo "OK: All health checks passed"
exit 0
EOF

chmod +x ~/Sentient-Core-v4/scripts/health_check.sh
```

### Run Health Check

```bash
# Manual health check
~/Sentient-Core-v4/scripts/health_check.sh

# Schedule periodic health checks (every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/mz1312/Sentient-Core-v4/scripts/health_check.sh >> /home/mz1312/Sentient-Core-v4/logs/health_check.log 2>&1") | crontab -
```

### System Metrics

```bash
# CPU usage
top -bn1 | grep "sentient"

# Memory usage
ps aux | grep sentient_aura_main.py | awk '{print $4, $6}'

# Network connections
ss -tn | grep :8765

# USB device bandwidth
lsusb -t
```

### Create Monitoring Dashboard

```bash
cat > ~/Sentient-Core-v4/scripts/monitor.sh << 'EOF'
#!/bin/bash
#
# Sentient Core Real-Time Monitor
#

watch -n 1 -t '
echo "=== SENTIENT CORE MONITOR ==="
echo ""
echo "Service Status:"
systemctl status sentient-core.service --no-pager | head -3
echo ""
echo "System Resources:"
echo "  CPU Temp: $(vcgencmd measure_temp)"
echo "  Memory: $(free -h | grep Mem | awk '"'"'{print $3 " / " $2}'"'"')"
echo "  Load: $(uptime | awk -F"load average:" '"'"'{print $2}'"'"')"
echo ""
echo "Coral TPU:"
lsusb | grep "18d1:9302" || echo "  Not detected"
echo ""
echo "WebSocket Connections:"
ss -tn | grep :8765 | wc -l
echo ""
echo "Recent Errors:"
sudo journalctl -u sentient-core.service -n 3 --no-pager | grep -i error || echo "  None"
'
EOF

chmod +x ~/Sentient-Core-v4/scripts/monitor.sh
```

Run monitor:
```bash
~/Sentient-Core-v4/scripts/monitor.sh
```

---

## Log Management

### Configure Log Rotation

```bash
sudo tee /etc/logrotate.d/sentient-core << 'EOF'
/home/mz1312/Sentient-Core-v4/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 mz1312 mz1312
    sharedscripts
    postrotate
        systemctl reload sentient-core.service > /dev/null 2>&1 || true
    endscript
}
EOF
```

### View Logs

```bash
# System journal (last 100 lines)
sudo journalctl -u sentient-core.service -n 100

# System journal (last hour)
sudo journalctl -u sentient-core.service --since "1 hour ago"

# System journal (follow live)
sudo journalctl -u sentient-core.service -f

# Application logs
tail -f ~/Sentient-Core-v4/logs/sentient_core.log

# Filter errors only
sudo journalctl -u sentient-core.service -p err
```

### Log Analysis

```bash
# Count errors in last hour
sudo journalctl -u sentient-core.service --since "1 hour ago" | grep -i error | wc -l

# Find most common errors
sudo journalctl -u sentient-core.service --since "24 hours ago" | \
    grep -i error | \
    awk '{print $0}' | \
    sort | uniq -c | sort -rn | head -10

# Check for memory warnings
sudo journalctl -u sentient-core.service | grep -i "memory\|oom"

# Check for device disconnects
sudo journalctl -u sentient-core.service | grep -i "disconnect\|usb.*removed"
```

---

## Backup and Recovery

### Backup Strategy

```bash
# Create backup script
cat > ~/Sentient-Core-v4/scripts/backup.sh << 'EOF'
#!/bin/bash
#
# Backup Sentient Core Configuration and Models
#

BACKUP_DIR="/home/mz1312/backups/sentient-core"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/sentient-core_${TIMESTAMP}.tar.gz"

mkdir -p "$BACKUP_DIR"

echo "Creating backup: $BACKUP_FILE"

tar -czf "$BACKUP_FILE" \
    -C /home/mz1312/Sentient-Core-v4 \
    config/ \
    models/*.tflite \
    arduino/ \
    .env \
    2>/dev/null || true

# Keep only last 7 backups
cd "$BACKUP_DIR"
ls -t sentient-core_*.tar.gz | tail -n +8 | xargs rm -f 2>/dev/null || true

echo "Backup complete: $(du -h $BACKUP_FILE | awk '{print $1}')"
EOF

chmod +x ~/Sentient-Core-v4/scripts/backup.sh
```

### Automated Backups

```bash
# Schedule daily backups at 2 AM
(crontab -l 2>/dev/null; echo "0 2 * * * /home/mz1312/Sentient-Core-v4/scripts/backup.sh") | crontab -
```

### Restore from Backup

```bash
# List available backups
ls -lh ~/backups/sentient-core/

# Restore from backup
BACKUP_FILE="~/backups/sentient-core/sentient-core_YYYYMMDD_HHMMSS.tar.gz"

# Stop service
sudo systemctl stop sentient-core.service

# Extract backup
cd ~/Sentient-Core-v4
tar -xzf "$BACKUP_FILE"

# Start service
sudo systemctl start sentient-core.service
```

---

## Performance Tuning

### CPU Governor

```bash
# Set performance governor
echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Make permanent
sudo apt install -y cpufrequtils
echo 'GOVERNOR="performance"' | sudo tee /etc/default/cpufrequtils
sudo systemctl restart cpufrequtils
```

### USB Power Management

```bash
# Disable USB autosuspend (prevents Coral disconnects)
echo 'SUBSYSTEM=="usb", TEST=="power/control", ATTR{power/control}="on"' | \
    sudo tee /etc/udev/rules.d/50-usb-power.rules

sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Network Tuning

```bash
# Increase network buffer sizes for WebSocket performance
sudo sysctl -w net.core.rmem_max=16777216
sudo sysctl -w net.core.wmem_max=16777216

# Make permanent
echo "net.core.rmem_max=16777216" | sudo tee -a /etc/sysctl.conf
echo "net.core.wmem_max=16777216" | sudo tee -a /etc/sysctl.conf
```

### GPU Memory Split

```bash
# Reduce GPU memory (we don't need it for AI workload)
sudo raspi-config nonint do_memory_split 16

# Reboot to apply
sudo reboot
```

### Swap Configuration

```bash
# Reduce swappiness (prefer RAM over swap)
sudo sysctl -w vm.swappiness=10

# Make permanent
echo "vm.swappiness=10" | sudo tee -a /etc/sysctl.conf
```

---

## Firewall Configuration

### Configure UFW (Optional)

```bash
# Install UFW if not present
sudo apt install -y ufw

# Allow SSH
sudo ufw allow 22/tcp

# Allow WebSocket port
sudo ufw allow 8765/tcp

# Enable firewall
sudo ufw --force enable

# Check status
sudo ufw status
```

---

## Troubleshooting Production Issues

### Service Won't Start

```bash
# Check service status
sudo systemctl status sentient-core.service

# View detailed logs
sudo journalctl -xe -u sentient-core.service

# Check file permissions
ls -la /home/mz1312/Sentient-Core-v4/launch_enhanced.sh

# Verify Python environment
/home/mz1312/.pyenv/versions/coral-py39/bin/python --version
```

### High CPU Usage

```bash
# Check CPU usage by process
top -bn1 | grep python

# Check if Coral TPU is being used (should be low CPU)
sudo journalctl -u sentient-core.service | grep "Coral TPU"

# If high CPU, check for CPU fallback mode
sudo journalctl -u sentient-core.service | grep "fallback"
```

### Memory Leaks

```bash
# Monitor memory over time
watch -n 5 'ps aux | grep sentient_aura_main.py | awk '"'"'{print $4, $6}'"'"''

# If memory grows continuously:
# 1. Restart service: sudo systemctl restart sentient-core.service
# 2. Check for WebSocket connection leaks
# 3. Review code for unclosed resources
```

### Coral TPU Disconnects

```bash
# Check dmesg for USB errors
dmesg | tail -30 | grep -i usb

# Check if autosuspend is disabled
cat /sys/bus/usb/devices/*/power/control

# If shows "auto", disable it:
echo 'on' | sudo tee /sys/bus/usb/devices/*/power/control
```

---

## Production Checklist

Before marking system as production-ready:

- [ ] systemd service installed and enabled
- [ ] Service survives reboot
- [ ] Health checks passing
- [ ] Logs rotating properly
- [ ] Automated backups configured
- [ ] Monitoring dashboard accessible
- [ ] CPU governor set to performance
- [ ] USB autosuspend disabled
- [ ] Firewall configured (if needed)
- [ ] Resource limits appropriate
- [ ] Error recovery tested
- [ ] 24-hour stability test passed

---

## Maintenance Schedule

### Daily
- Health check automated via cron
- Review error logs

### Weekly
- Check disk space: `df -h`
- Review system logs: `sudo journalctl -u sentient-core.service --since "7 days ago" | grep -i error`
- Verify backup completed: `ls -lh ~/backups/sentient-core/`

### Monthly
- Update system packages: `sudo apt update && sudo apt upgrade`
- Review performance metrics
- Clean old logs: `sudo journalctl --vacuum-time=30d`
- Test backup restore procedure

### Quarterly
- Review and update configuration
- Test failover scenarios
- Update Python dependencies (carefully)
- Re-train Coral model with new data (if applicable)

---

## Next Steps

Your Enhanced Sentient Core is now production-ready! 🎉

**Access your system**:
- WebSocket: `ws://sentient-core.local:8765`
- Visualization: `file:///home/mz1312/Sentient-Core-v4/sentient_aura/sentient_core.html`
- Logs: `sudo journalctl -u sentient-core.service -f`

**Useful commands**:
```bash
# Quick status
systemctl status sentient-core.service

# Monitor in real-time
~/Sentient-Core-v4/scripts/monitor.sh

# Health check
~/Sentient-Core-v4/scripts/health_check.sh
```
