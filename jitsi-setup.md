# Jitsi Self-Hosting Blueprint (Docker)

To make the **Host Moderator** status work automatically, you must run your own Jitsi instance. This setup will verify your Django JWTs.

## 1. Get the official Jitsi Docker setup
```bash
git clone https://github.com/jitsi/docker-jitsi-meet
cd docker-jitsi-meet
cp env.example .env
```

## 2. Configure for JWT Authentication
Edit the `.env` in the `docker-jitsi-meet` folder:

```properties
# Essential Settings
PUBLIC_URL=https://meet.yourdomain.com
ENABLE_AUTH=1
ENABLE_GUESTS=1
AUTH_TYPE=jwt

# JWT Settings (MUST MATCH DJANGO)
JWT_APP_ID=my_django_app
JWT_APP_SECRET=62HfvFanpSC2OCCFIGV28YurmPRLP8_d51OlOWcrk5Q
JWT_ACCEPTED_ISSUERS=my_django_app
JWT_ACCEPTED_AUDIENCES=jitsi
```

## 3. Run Jitsi
```bash
docker-compose up -d
```

## 4. Update your Django .env
```properties
JITSI_DOMAIN=meet.yourdomain.com
JITSI_APP_ID=my_django_app
JITSI_APP_SECRET=62HfvFanpSC2OCCFIGV28YurmPRLP8_d51OlOWcrk5Q
```

## Why this is necessary?
Public Jitsi (`meet.jit.si`) forbids anonymous moderators to prevent spam. By running the above, you become the **authority**, and your Django server can tell Jitsi exactly who the moderator is.
