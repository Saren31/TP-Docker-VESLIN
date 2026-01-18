# TP Optimisation Docker - Rendu de Lucas Veslin
  
## Optimisation du Dockerfile

### Etape 0 : Baseline (Dockerfile initial)

- Temps de build : **10.9s**
- Taille de l'image : **1.72GB**

```bash
docker build --no-cache -t tp-optimisation:test0 .
```

On utilise l'option no-cache pour éviter de réutiliser les layers déjà existants et obtenir un temps de build plus pertinent.

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

On utilise maintenant le multistage pour séparer la partie build de la partie exécution. Le premier stage contient l'ensemble des dépendances et des outils nécessaire à la compilation alors que le deuxième stage contient seulement ce qui est nécessaire pour exécuter l'application.

En faisant cela, on réduit grandement la taille de l'image finale. On utilise aussi une image alpine afin d'alléger davantage l'image.

De plus, on choisit une version d'image fixe pour node pour avoir plus de stabilité.

### Etape 2 : Fusion des lignes RUN

- Temps de build : **9.7s**
- Taille de l'image : **210MB**

```bash
docker build --no-cache -t tp-optimisation:test2 .
```

Résultat du temps de build :
```bash
Building 9.7s (16/16) FINISHED
```

Résultat de la taille de l'image :
```bash
IMAGE                   ID             DISK USAGE   CONTENT SIZE   EXTRA
tp-optimisation:test0   b09119868fb8       1.72GB          433MB    U 
tp-optimisation:test1   9148842b5140        210MB         50.4MB
tp-optimisation:test2   b456e73e7b78        210MB         50.4MB

```

Dockerfile : 

```dockerfile
FROM node:20 AS builder
WORKDIR /app
COPY node_modules ./node_modules
COPY . /app
ENV NODE_ENV=development
RUN npm install && \ 
	apt-get update && \
	apt-get install -y build-essential ca-certificates locales && \ 
	echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen && \
	npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app ./app
EXPOSE 3000 4000 5000
ENV NODE_ENV=development
USER root
CMD ["node", "app/server.js"]
```

Les commandes RUN ont été fusionnées pour réduire le nombre de layers.

Dans ce cas, la taille de l'image n'est pas réduite mais temps de build est légèremment plus court.

### Etape 3 : Copie intelligente des fichiers

- Temps de build : **9.7s**
- Taille de l'image : **210MB**

```bash
docker build --no-cache -t tp-optimisation:test3 .
```

Résultat du temps de build :
```bash
Building 9.7s (14/14 ) FINISHED
```

Résultat de la taille de l'image :
```bash
IMAGE                   ID             DISK USAGE   CONTENT SIZE   EXTRA
tp-optimisation:test0   b09119868fb8       1.72GB          433MB    U 
tp-optimisation:test1   9148842b5140        210MB         50.4MB
tp-optimisation:test2   b456e73e7b78        210MB         50.4MB
tp-optimisation:test3   6411b0a6e016        210MB         50.5MB
```

Dockerfile : 

```dockerfile
FROM node:20 AS builder
WORKDIR /app
ENV NODE_ENV=development

COPY package*.json .

RUN npm install && \ 
	apt-get update && \
	apt-get install -y build-essential ca-certificates locales && \ 
	echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen && \
	npm run build
	
COPY . .


FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app ./app
EXPOSE 3000 4000 5000
ENV NODE_ENV=development
USER root
CMD ["node", "app/server.js"]
```

On arrête de copier le dossier node_modules depuis notre machine car il est recréé dans l'image avec la commande npm install. 
On copie les 2 fichiers package en premier afin d'optimiser. 
Le reste des fichiers est copié après le build.

### Etape 4 : Utilisation du .dockerignore

- Temps de build : **9.7s**
- Taille de l'image : **210MB**

```bash
docker build --no-cache -t tp-optimisation:test3 .
```

Résultat du temps de build :
```bash
Building 9.7s (14/14 ) FINISHED
```

Résultat de la taille de l'image :
```bash
IMAGE                   ID             DISK USAGE   CONTENT SIZE   EXTRA
tp-optimisation:test0   b09119868fb8       1.72GB          433MB    U 
tp-optimisation:test1   9148842b5140        210MB         50.4MB
tp-optimisation:test2   b456e73e7b78        210MB         50.4MB
tp-optimisation:test3   6411b0a6e016        210MB         50.5MB
tp-optimisation:test4   d984f3c61a0c        210MB         50.4MB
```

.dockerignore : 

```dockerfile
node_modules
```

On utilise le fichier .dockerignore pour exclure les fichiers inutiles lors du build. Cela n'impacte pas les performances, ni la taille de l'image dans ce cas, mais c'est plus propre.

### Conclusion

Les principales optimisations ont été appliquées : multistage, image alpine, moins de layers et meilleure gestion des fichiers copiés.

Il me semble difficile d'améliorer vraiment les performances ou la taille maintenant avec mes connaissances.

Dockerfile final :
```dockerfile
FROM node:20 AS builder
WORKDIR /app
ENV NODE_ENV=development

COPY package*.json .

RUN npm install && \ 
	apt-get update && \
	apt-get install -y build-essential ca-certificates locales && \ 
	echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen && \
	npm run build
	
COPY . .


FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app ./app
EXPOSE 3000 4000 5000
ENV NODE_ENV=development
USER root
CMD ["node", "app/server.js"]
```