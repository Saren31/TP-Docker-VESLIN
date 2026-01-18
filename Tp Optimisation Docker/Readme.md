# TP Optimisation Docker - Rendu de Lucas Veslin
  
## Optimisation du Dockerfile

### Etape 0 : Baseline (Dockerfile initial)

- Temps de build : **10.9s**
- Taille de l'image : **1.72GB**

```bash
docker build --no-cache -t tp-optimisation:test0 .
```

On utilise l'option no-cache pour éviter de réutiliser les layers déjà créés lors du build.

Résultat du temps de build :
```bash
Building 10.9s (12/12) FINISHED
```

Résultat de la taille de l'image :
```bash
IMAGE                   ID             DISK USAGE   CONTENT SIZE   EXTRA
tp-optimisation:test0   b09119868fb8       1.72GB          433MB
```

Dockerfile : 
```dockerfile
FROM node:latest
WORKDIR /app
COPY node_modules ./node_modules
COPY . /app
RUN npm install
RUN apt-get update && apt-get install -y build-essential ca-certificates locales && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen
EXPOSE 3000 4000 5000
ENV NODE_ENV=development
RUN npm run build
USER root
CMD ["node", "server.js"]
```

On utilise le Dockerfile donné et on considère que l'image de base est déjà téléchargé pour ne pas fausser le temps de build.

### Etape 1 : Multistage

- Temps de build : **10.1s**
- Taille de l'image : **210MB**

```bash
docker build --no-cache -t tp-optimisation:test1 .
```

Résultat du temps de build :
```bash
Building 10.1s (16/16) FINISHED               
```

Résultat de la taille de l'image :
```bash
IMAGE                   ID             DISK USAGE   CONTENT SIZE   EXTRA
tp-optimisation:test0   b09119868fb8       1.72GB          433MB    U 
tp-optimisation:test1   9148842b5140        210MB         50.4MB
```

Dockerfile : 

```dockerfile
FROM node:20 AS builder
WORKDIR /app
COPY node_modules ./node_modules
COPY . /app
RUN npm install
RUN apt-get update && apt-get install -y build-essential ca-certificates locales && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen
ENV NODE_ENV=development
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app ./app
EXPOSE 3000 4000 5000
ENV NODE_ENV=development
USER root
CMD ["node", "app/server.js"]
```

On utilise maintenant le multistage pour séparer la partie compilation de la partie exécution. Le premier stage contient l'ensemble des dépendances et des outils nécessaire pour faire le build alors que le deuxième stage contient seulement ce qui est nécessaire pour l'exécution.

En faisant cela, on réduit grandement la taille de l'image finale sans rien perdre. On choisit une image alpine pour qu'elle soit plus légère.

De plus, on choisit une version d'image fixe pour node pour avoir plus de stabilité.