# 🚀 MCP 게시판 AWS Lightsail 배포 가이드

## 📋 목차
- [시스템 요구사항](#-시스템-요구사항)
- [Lightsail 인스턴스 사양](#-lightsail-인스턴스-사양)
- [배포 준비](#-배포-준비)
- [실제 배포 과정](#-실제-배포-과정)
- [배포 후 설정](#-배포-후-설정)
- [보안 설정](#-보안-설정)
- [모니터링 및 관리](#-모니터링-및-관리)
- [문제해결](#-문제해결)

---

## 💻 시스템 요구사항

### Python 환경
- **Python**: 3.8 이상 (권장: 3.10+)
- **OS**: Ubuntu 22.04 LTS
- **메모리**: 최소 512MB (권장: 1GB 이상)

### 필수 의존성
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
jinja2==3.1.2
python-multipart==0.0.6
pydantic==2.5.0
python-dotenv==1.0.0
aiofiles==23.2.1
anthropic==0.40.0
```

---

## 💻 Lightsail 인스턴스 사양

### 💰 요금제별 추천

| 사양 | 요금 | RAM | CPU | SSD | 용도 |
|------|------|-----|-----|-----|------|
| 최소 | $3.50/월 | 512MB | 1vCPU | 20GB | 개발/테스트 |
| **권장** | **$5/월** | **1GB** | **1vCPU** | **40GB** | **실운영** ⭐ |
| 안정적 | $10/월 | 2GB | 1vCPU | 60GB | 트래픽 많음 |

> **추천**: $5/월 플랜이 MCP 게시판 운영에 최적화되어 있습니다.

---

## 🛠 배포 준비

### 1. 프로덕션용 실행 스크립트 생성

**파일명**: `start_server.py`
```python
#!/usr/bin/env python3
"""
프로덕션 환경용 서버 시작 스크립트
"""

import uvicorn
from app import app
from config import config

if __name__ == "__main__":
    print("🚀 MCP 게시판 프로덕션 서버를 시작합니다...")
    
    # 프로덕션 환경 설정
    uvicorn.run(
        "app:app",
        host=config.HOST,
        port=config.PORT,
        reload=False,  # 프로덕션에서는 reload 비활성화
        access_log=True,
        log_level="info",
        workers=1  # 단일 워커 (Lightsail 1GB RAM 고려)
    )
```

### 2. systemd 서비스 파일

**파일명**: `mcp-board.service`
```ini
[Unit]
Description=MCP Board FastAPI Application
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/mcp_board
Environment=PATH=/home/ubuntu/mcp_board/venv/bin
ExecStart=/home/ubuntu/mcp_board/venv/bin/python start_server.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 3. Nginx 리버스 프록시 설정

**파일명**: `nginx.conf`
```nginx
server {
    listen 80;
    server_name your-domain.com;  # 실제 도메인으로 변경

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 정적 파일 직접 서빙
    location /static {
        alias /home/ubuntu/mcp_board/static;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 4. 배포 자동화 스크립트

**파일명**: `deploy.sh`
```bash
#!/bin/bash

# MCP 게시판 Lightsail 배포 스크립트

echo "🚀 MCP 게시판 배포를 시작합니다..."

# 1. 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# 2. Python 3.10+ 설치
sudo apt install -y python3 python3-pip python3-venv git nginx htop

# 3. 프로젝트 디렉토리 생성
cd /home/ubuntu
git clone https://github.com/your-username/mcp_board.git
cd mcp_board

# 4. 가상환경 생성 및 의존성 설치
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. 환경 변수 설정
cat > .env << EOF
ANTHROPIC_API_KEY=your_api_key_here
HOST=0.0.0.0
PORT=8000
DEBUG=false
DATABASE_URL=sqlite:///board.db
MCP_ENABLED=true
DEFAULT_MODEL=claude-3-5-sonnet-20241022
SECRET_KEY=$(openssl rand -hex 32)
EOF

# 6. 데이터베이스 초기화
python3 -c "from database import init_sample_data; init_sample_data()"

# 7. systemd 서비스 등록
sudo cp mcp-board.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mcp-board

# 8. Nginx 설정
sudo cp nginx.conf /etc/nginx/sites-available/mcp-board
sudo ln -sf /etc/nginx/sites-available/mcp-board /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# 9. 방화벽 설정
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# 10. 서비스 시작
sudo systemctl start mcp-board

echo "✅ 배포가 완료되었습니다!"
echo "🌐 브라우저에서 http://$(curl -s ifconfig.me) 로 접속하세요"
echo "📊 서비스 상태: sudo systemctl status mcp-board"
```

---

## 🚀 실제 배포 과정

### 1단계: Lightsail 인스턴스 생성

1. **AWS 콘솔** → **Lightsail** 접속
2. **"인스턴스 생성"** 클릭
3. **설정 선택**:
   - **플랫폼**: Linux/Unix
   - **Blueprint**: Ubuntu 22.04 LTS
   - **플랜**: $5/월 (1GB RAM, 1vCPU, 40GB SSD)
   - **인스턴스 이름**: `mcp-board`
4. **SSH 키페어** 다운로드 보관

### 2단계: SSH 연결 및 프로젝트 업로드

```bash
# SSH 연결
ssh -i your-key.pem ubuntu@your-lightsail-ip

# 프로젝트 업로드 (방법 1: Git 사용)
git clone https://github.com/your-username/mcp_board.git
cd mcp_board

# 또는 (방법 2: SCP로 직접 업로드)
# 로컬에서 실행:
# scp -i your-key.pem -r ./mcp_board ubuntu@your-ip:/home/ubuntu/
```

### 3단계: 자동 배포 실행

```bash
# 배포 스크립트 실행 권한 부여
chmod +x deploy.sh

# 배포 실행
./deploy.sh
```

### 4단계: API 키 설정

```bash
# 환경 변수 파일 편집
nano .env

# 다음 라인 수정:
# ANTHROPIC_API_KEY=sk-ant-api03-your_actual_key_here
```

### 5단계: 서비스 시작

```bash
# 서비스 재시작
sudo systemctl restart mcp-board

# 상태 확인
sudo systemctl status mcp-board
```

---

## ⚙️ 배포 후 설정

### 도메인 연결 (선택사항)

1. **Lightsail 고정 IP 할당**:
   ```bash
   # Lightsail 콘솔에서 고정 IP 생성 및 연결
   ```

2. **DNS 설정**:
   - 도메인 등록업체에서 A 레코드 추가
   - `your-domain.com` → `your-lightsail-ip`

3. **Nginx 설정 업데이트**:
   ```bash
   sudo nano /etc/nginx/sites-available/mcp-board
   # server_name을 실제 도메인으로 변경
   sudo systemctl reload nginx
   ```

### HTTPS 설정 (SSL/TLS)

```bash
# Certbot 설치
sudo apt install certbot python3-certbot-nginx

# SSL 인증서 발급
sudo certbot --nginx -d your-domain.com

# 자동 갱신 설정
sudo crontab -e
# 추가: 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 🔒 보안 설정

### 방화벽 구성

```bash
# UFW 방화벽 설정
sudo ufw allow 22     # SSH
sudo ufw allow 80     # HTTP
sudo ufw allow 443    # HTTPS
sudo ufw deny 8000    # FastAPI 직접 접근 차단
sudo ufw --force enable

# 현재 상태 확인
sudo ufw status
```

### 파일 권한 설정

```bash
# 환경 변수 파일 보안
chmod 600 .env
chown ubuntu:ubuntu .env

# 로그 디렉토리 생성
sudo mkdir -p /var/log/mcp-board
sudo chown ubuntu:ubuntu /var/log/mcp-board
```

### SSH 보안 강화

```bash
# SSH 설정 수정
sudo nano /etc/ssh/sshd_config

# 다음 설정 추가/수정:
# PermitRootLogin no
# PasswordAuthentication no
# AllowUsers ubuntu

# SSH 재시작
sudo systemctl restart ssh
```

---

## 📊 모니터링 및 관리

### 서비스 상태 확인

```bash
# 서비스 상태
sudo systemctl status mcp-board

# 실시간 로그 확인
sudo journalctl -u mcp-board -f

# Nginx 상태
sudo systemctl status nginx
```

### 리소스 모니터링

```bash
# 시스템 리소스 확인
htop
df -h
free -h

# 네트워크 상태
sudo netstat -tlnp | grep :8000
```

### 로그 관리

```bash
# 로그 로테이션 설정
sudo nano /etc/logrotate.d/mcp-board

# 내용:
/var/log/mcp-board/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    sharedscripts
}
```

### 백업 설정

```bash
# 데이터베이스 백업 스크립트
cat > /home/ubuntu/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp /home/ubuntu/mcp_board/board.db /home/ubuntu/backups/board_$DATE.db
# 7일 이상 된 백업 파일 삭제
find /home/ubuntu/backups/ -name "board_*.db" -mtime +7 -delete
EOF

chmod +x /home/ubuntu/backup.sh
mkdir -p /home/ubuntu/backups

# 일일 백업 크론탭 설정
crontab -e
# 추가: 0 2 * * * /home/ubuntu/backup.sh
```

---

## 🔧 문제해결

### 일반적인 문제들

#### 1. 서비스가 시작되지 않는 경우

```bash
# 로그 확인
sudo journalctl -u mcp-board --no-pager

# 직접 실행으로 에러 확인
cd /home/ubuntu/mcp_board
source venv/bin/activate
python start_server.py
```

#### 2. 데이터베이스 오류

```bash
# 데이터베이스 재초기화
cd /home/ubuntu/mcp_board
source venv/bin/activate
python -c "from database import init_sample_data; init_sample_data()"
```

#### 3. Nginx 502 오류

```bash
# Nginx 설정 테스트
sudo nginx -t

# 포트 확인
sudo netstat -tlnp | grep :8000

# 서비스 재시작
sudo systemctl restart mcp-board nginx
```

#### 4. API 키 오류

```bash
# 환경 변수 확인
cd /home/ubuntu/mcp_board
source venv/bin/activate
python -c "from config import config; print(f'API Key configured: {config.is_api_key_configured()}')"
```

### 성능 최적화

```bash
# 스왑 설정 (메모리 부족시)
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 스왑 사용량 조절
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
```

---

## 💰 비용 관리

### 예상 월 비용
- **Lightsail 인스턴스**: $5/월
- **데이터 전송**: 무료 (1TB까지)
- **도메인**: $10-15/년 (선택사항)
- **총 예상 비용**: 월 $5-10

### 비용 최적화 팁
1. **CloudWatch 알람** 설정으로 리소스 사용량 모니터링
2. **정기 스냅샷** 생성으로 데이터 백업
3. **로그 크기 관리**로 디스크 공간 절약

---

## 🎯 마무리

이 가이드를 따라하면 AWS Lightsail에서 안정적인 MCP 게시판 서비스를 운영할 수 있습니다.

### 배포 후 확인사항
- [ ] 웹사이트 접속 확인 (`http://your-ip`)
- [ ] API 키 설정 확인
- [ ] 게시글 작성/조회 테스트
- [ ] 차트 생성 기능 테스트
- [ ] 서비스 자동 시작 확인 (`sudo systemctl is-enabled mcp-board`)

### 문제 발생시
1. 로그 확인: `sudo journalctl -u mcp-board -f`
2. 서비스 재시작: `sudo systemctl restart mcp-board`
3. GitHub Issues에 문제 보고

**🎉 배포 완료! 이제 MCP 게시판을 실제 서비스로 운영할 수 있습니다!**