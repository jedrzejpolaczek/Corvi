# Cloud Deployment Guide (Docker + VPS/Cloud)

## ✅ What You Need

- Cloud VPS (e.g., Linode, DigitalOcean, AWS EC2, Google VM, Hetzner)
- Docker installed on the server
- Docker Compose installed
- Open port `8000` or reverse proxy (NGINX)
- (Optional) Custom domain + HTTPS

---

## 🚀 1. Choose Cloud Server

Use any VPS with Ubuntu 22.04 LTS.

---

## ⚙️ 2. Install Docker and Docker Compose

Connect via SSH:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER
newgrp docker
```

Check versions:

```bash
docker --version
docker-compose --version
```

---

## 📦 3. Upload the Project

From local machine:

```bash
scp hyperopt_saas.zip username@your-server-ip:~
ssh username@your-server-ip
unzip hyperopt_saas.zip
cd hyperopt_saas
```

Or clone:

```bash
git clone https://github.com/yourusername/hyperopt_saas.git
cd hyperopt_saas
```

---

## 🏗️ 4. Start the App

On server:

```bash
docker-compose up --build -d
```

Check containers:

```bash
docker-compose ps
```

---

## 🌐 5. Access the App

Open in browser:

```
http://your-server-ip:8000
```

> 🛡️ Optional: set up HTTPS + domain (see below)

---

## ✅ 6. Done!

- You can now upload files and get optimization results.
- Logs:

```bash
docker-compose logs -f
```

---

## 📌 Optional: Domain + HTTPS (NGINX + Certbot)

1. Install NGINX + Certbot:

```bash
sudo apt install nginx certbot python3-certbot-nginx
```

2. Create config `/etc/nginx/sites-available/yourdomain.com`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. Enable and secure with HTTPS:

```bash
sudo ln -s /etc/nginx/sites-available/yourdomain.com /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d yourdomain.com
```

---

## 🔄 Tips

- Use Docker Volumes or S3 to store `results/`
- Use systemd or supervisor to auto-restart Docker
- Use `ufw` or firewall to restrict open ports

---

## 🧱 Advanced

- Kubernetes + Load Balancer
- AWS/GCP Deployment Templates
- User auth with OAuth2/JWT